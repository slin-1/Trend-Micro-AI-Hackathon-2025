def markdownify_list(l):
    output = ''
    for i, element in enumerate(l):
        output += f"{i+1}. {element}\n"
    return output + '\n'
