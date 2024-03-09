from FuzzingCoverage import Coverage
import json

def is_interesting(func, input, global_map, buckets):
    # perform coverage test
    with Coverage() as cov:
        func(input) # run the function
        
        shared_mem = {} # store tuple counts
        trace = cov.trace() # list of function name and line number in function

        for i in range(len(trace) - 1):
            # convert into a format that is unique for each tuple
            tuple_format = "{}-{}=>{}-{}".format(trace[i][0], trace[i][1], trace[i+1][0], trace[i+1][1])
            if tuple_format in shared_mem.keys():
                # increment value for tuple in shared_mem if it exists
                shared_mem[tuple_format] += 1
            else:
                # we start counting
                shared_mem[tuple_format] = 1

        # print(json.dumps(shared_mem,indent = 4, sort_keys=True))

        is_interesting_result = False

        # for each tuple we find in shared_mem
        for tuple_format in shared_mem.keys():
            if tuple_format not in global_map.keys():
                # if tuple does not exist in global_map, we create empty buckets for the tuple in global_map
                global_map[tuple_format] = [False] * len(buckets)
                # such result means that it is interesting by default
                is_interesting_result = True

            repetitions = shared_mem[tuple_format] # get the number of times a tuple has been hit

            # we iterate through the bucket counts and check our number of repetitions fall into which bucket
            for index, bucket_count in enumerate(buckets):
                if repetitions < bucket_count:                          
                    # checks if the number of repetitions is smaller than a particular bucket count
                    # if it is, the previous bucket is the one we are looking for
                    # if our bucket is False, we mark it as interesting, and set then set it to True
                    # print(repetitions, tuple_format ,global_map[tuple_format], index-1)
                    if not global_map[tuple_format][index - 1]:
                        is_interesting_result = True
                        global_map[tuple_format][index - 1] = True
                        # print("Interesting!")
                    break
                    # if our tuple bucket is already True, it's not interesting. we don't do anything
            # print("Not interesting")

        return is_interesting_result