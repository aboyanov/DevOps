def gen_nums():
    n = 0
    while n < 4:
        yield n
        n += 1
        
nums = gen_nums()
print(nums)
print(type(nums))