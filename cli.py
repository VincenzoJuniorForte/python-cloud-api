import argparse
from main import calculate

parser = argparse.ArgumentParser()
parser.add_argument('-op', '--operation', type=str, help='initial operation')
parser.add_argument('-step', '--step', type=str, help='last input from user')
parser.add_argument('-task', '--task', default='expand', type=str, help='extra input from exercise instructions')
args = parser.parse_args()

operation = args.operation
step = args.step
task = args.task

solution, is_correct, is_true = calculate(operation, step, task)

print(solution, is_correct, is_true)
