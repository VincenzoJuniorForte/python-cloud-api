import os
import openai
import json
import pandas as pd
import time
import argparse
from embedding import get_embeddings, get_most_similar

parser = argparse.ArgumentParser()
# if an argument is passed in as True, we do it
parser.add_argument("--Explain", default=False, type=bool)
parser.add_argument("--Do_MATH", default=True, type=bool)
parser.add_argument("--Do_Courses", default=False, type=bool)
args = parser.parse_args()

column_labels = ["Topic", 'Question', 'Solution', 'Codex Solution']
if args.Explain:
    column_labels += ['Codex Explanation Input', 'Codex Explanation']
# column_labels += ['Most Similar Questions']

openai.api_key = os.getenv('OpenAI_API_Key')
courses_to_zero_shot = ['18.01', '18.02', '18.03', '6.042', '18.05', '18.06', 'COMS3251']
# MATH_sections_to_zero_shot = ['Algebra', 'Counting & Probability', 'Intermediate Algebra',
#                               'Number Theory', 'Prealgebra', 'Precalculus']
MATH_sections_to_zero_shot = ['Algebra', 'Prealgebra', 'Precalculus']
questions_per_course = 25
questions_per_MATH_section = 15
gpt_engine = "gpt-3.5-turbo"
engine_temperature = 0
engine_topP = 0
zero_shot_max_tokens = 256
explanation_max_tokens = 150
time_delay = 61

#locations of embeddings and which indexes refer to which questions
courses_embeddings_location = 'course_embeddings.json'
courses_embeddings_indexes = {'18.01':[0, 24], '18.02':[25, 49],
                              '18.03':[50, 74], '6.042': [75,99],
                              '18.05':[100, 124], '18.06':[125, 149],
                              'COMS3251':[150,174]}
MATH_embeddings_location = 'MATH_embeddings.json'
MATH_embeddings_indexes = {'MATH_Algebra':[0, 14], 'MATH_Counting_&_Probability':[15, 29],
                           'MATH_Intermediate_Algebra':[30, 44], 'MATH_Number_Theory':[45, 59],
                           'MATH_Prealgebra':[60, 74], 'MATH_Precalculus':[75, 89]}

# for prompt formatting:
docstring_front = 'Solve the following problem:\n'
context_array = ['write a program', 'using sympy', 'using simulations']
explanation_suffix = "\n\n'''\nHere's what the above code is doing:\n1."
messages_prompt = [{"role": "user"}]
step_context = "Show me the solution step by step."
use_sympy = "Make sure the result is correct by writing a python program using sympy that solves the problem, and show me the code."

def execute_zero_shot(courses, questions_per,
                      embeddings_location, embeddings_indexes):
    """
    Runs zero-shot on questions_per questions for each course in courses.
    An individual CSV file of the results is made for each course in courses.
    The embeddings for all of the questions for all of the courses in courses are located in embeddings_location.
    """
    # all_embeddings = get_embeddings(embeddings_location)
    math_df = pd.read_csv("MATH.csv")
    for course in courses:
        # course_embeddings = all_embeddings[embeddings_indexes[course][0]:embeddings_indexes[course][1]+1]
        topic_df = math_df[math_df["Topic"] == course]
        rows = []
        print("\n\n")
        for i in range(len(topic_df)):
            question = topic_df["Original Problem"].iloc[i]
            codex_solution = topic_df["Solution"].iloc[i]
            print('Running Zero-Shot on ' + course + ', question ' + str(i))
            start = time.time()

             #to avoid an openai.error.RateLimitError
            codex_input = docstring_front + ' ' + question + step_context + use_sympy
            messages_prompt[0]["content"] = codex_input
            gpt_output = openai.Completion.create(engine = gpt_engine,
                                                    messages = messages_prompt,
                                                    max_tokens = zero_shot_max_tokens,
                                                    temperature = engine_temperature)['choices'][0]['message']["content"]
            row = [course, question, gpt_output, codex_solution]
            print(row)
            time.sleep(time_delay)
            if args.Explain:
                time.sleep(time_delay) #to avoid an openai.error.RateLimitError
                explanation_input = docstring_front + ' ' + question + step_context + use_sympy + explanation_suffix
                messages_prompt[0]["content"] = explanation_input
                explanation_output = openai.Completion.create(engine = gpt_engine,
                                                        messages = messages_prompt,
                                                        max_tokens = explanation_max_tokens,
                                                        temperature = engine_temperature)['choices'][0]['message']["content"]
                row += [explanation_input, explanation_output]

            # most_similar_questions = get_most_similar(course_embeddings,i)
            # row += [most_similar_questions]
            end = time.time()
            print('API call time: ' + str(end-start) + '\n')
            rows.append(row)
        info = pd.DataFrame(rows, columns=column_labels)
        course_results_location = course + ' results.csv'
        info.to_csv(course_results_location, index=False)

if __name__ == "__main__":
    #zero-shot step for courses:
    if args.Do_Courses:
        execute_zero_shot(courses_to_zero_shot, questions_per_course,
                          courses_embeddings_location, courses_embeddings_indexes)
    #zero-shot step for MATH benchmark:
    if args.Do_MATH:
        execute_zero_shot(MATH_sections_to_zero_shot, questions_per_MATH_section,
                          MATH_embeddings_location, MATH_embeddings_indexes)
