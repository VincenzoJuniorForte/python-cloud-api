import argparse
from main import *

parser = argparse.ArgumentParser()
parser.add_argument('-op', '--operation', type=str, help='initial operation')
parser.add_argument('-step', '--step', type=str, help='last input from user')
parser.add_argument('-task', '--task', default='expand', type=str, help='extra input from exercise instructions')
parser.add_argument('-last', '--last_correct', type=str, help='last correct step')
args = parser.parse_args()

operation = args.operation
step = args.step
task = args.task
last_correct = args.last_correct

solution, is_correct, is_true = calculate(operation, step, task)
new_step, new_string = next_step(last_correct)

print(solution, is_correct, is_true, new_string)
