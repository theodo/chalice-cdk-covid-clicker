import os

from aws_cdk import (
    aws_dynamodb as dynamodb,
    core as cdk,
)
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets

from chalice.cdk import Chalice

os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"  # new


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, "runtime"
)


class ChaliceApp(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.dynamodb_table = self._create_ddb_table()
        self.chalice = Chalice(
            self,
            "ChaliceApp",
            source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "environment_variables": {
                    "APP_TABLE_NAME": self.dynamodb_table.table_name,
                    "DYNAMODB_STREAM_ARN": self.dynamodb_table.table_stream_arn,
                }
            },
        )
        self.stepfunction = self._create_step_function()
        self.bus = self._create_bus()
        self._create_rule_and_target(self.bus,self.stepfunction)
        self.dynamodb_table.grant_read_write_data(self.chalice.get_role("DefaultRole"))

    def _create_ddb_table(self):
        dynamodb_table = dynamodb.Table(
            self,
            "AppTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        cdk.CfnOutput(self, "AppTableName", value=dynamodb_table.table_name)
        return dynamodb_table

    def _create_step_function(self):
        choose_wait_time = tasks.LambdaInvoke(self, "ChooseWaitTime",
                        lambda_function=self.chalice.get_function("ChooseWaitTime"),
                        result_selector={"x_seconds.$":"$.Payload"},
                        result_path="$")

        wait_x = sfn.Wait(self, 'Wait X Seconds',
                    time= sfn.WaitTime.seconds_path('$.x_seconds'))

        create_virus = tasks.LambdaInvoke(self, "CreateVirus",
                        lambda_function=self.chalice.get_function("CreateVirus"))

        success = sfn.Succeed(self, "VirusCreated")

        step_function_definition = choose_wait_time.next(wait_x).next(create_virus).next(success)

        state_machine = sfn.StateMachine(self, "CreateVirusMachine",
                        definition=step_function_definition)
        return state_machine

    def _create_bus(self):
        bus = events.EventBus(self,'eventBus',event_bus_name='eventBus')
        return bus

    def _create_rule_and_target(self,bus:events.EventBus,step_function:sfn.StateMachine):
        rule = events.Rule(self,'rule',event_bus=bus)
        rule.add_event_pattern(detail_type=['VIRUS_CREATION_REQUESTED'],source=['Time'])
        rule.add_target(targets.SfnStateMachine(step_function))
