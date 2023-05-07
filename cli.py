import argparse
from main import *

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--original', type=str, help='initial operation')
parser.add_argument('-s', '--step', type=str, help='last input from user')
parser.add_argument('-t', '--task', default='expand', type=str, help='extra input from exercise instructions')
parser.add_argument('-l', '--last_correct', type=str, help='last correct step')
args = parser.parse_args()

operation = args.original
step = args.step
task = args.task
last_correct = args.last_correct

solution, is_correct, is_true = calculate(operation, step, task)
new_step, new_string = next_step(last_correct)

print(solution, is_correct, is_true, new_string)
