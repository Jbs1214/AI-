colors = ["red", "green", "blue"]

print(colors[0:2:3])

colors.append("yellow")
print(colors)

colors.insert(0, "white")
print(colors)

colors.remove('white')
print(colors)

numbers = [8, 5, 3, 2, 7]
numbers.sort()
print(numbers)
numbers.sort(reverse=True)
print(numbers)
numbers.reverse()
print(numbers)
numbers.remove(2)
print(2 in numbers)