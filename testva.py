email1 = "samurai@ninja.edu"
email2 = "samurai@ninja.edu.in"
email3 = "samurai@ninja.ac.in"
college_email = email3.split('.')[-1:]
print(college_email)
if not (college_email == ['edu']):
    college_email = email3.split('.')[-2:]
    print(college_email)
    if not (college_email == ['edu', 'in'] or college_email == ['ac', 'in']):
        print("not allowed")