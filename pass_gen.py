def pass_gen(name, phone, roll):
    file = open("pass.html", "r")

    html = file.read()
    html = html.replace("{{name}}", name.upper())
    html = html.replace("{{phone}}", phone)
    html = html.replace("{{roll}}", roll.upper())

    file.close()

    return html