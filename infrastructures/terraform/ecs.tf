resource "aws_ecs_cluster" "instance" {
  name = var.project_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

//resource "aws_ecs_task_definition" "definition" {
//  container_definitions = jsonencode([])
//  family                = "brosfiles"
//}
//
//resource "aws_ecs_service" "brosfiles" {
//  name            = var.project_name
//  cluster         = aws_ecs_cluster.instance.id
//  task_definition = aws_ecs_task_definition.definition.arn
//  desired_count   = 3
//
//  ordered_placement_strategy {
//    type  = "binpack"
//    field = "cpu"
//  }
//}
