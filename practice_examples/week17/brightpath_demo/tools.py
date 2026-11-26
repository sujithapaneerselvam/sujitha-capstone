def lookup_policy():
    return "Eligible employees receive 20 days of paid annual leave per complete calendar year. Source: HR_02_Annual_Leave_Policy.txt"
def send_email(db, key, args):
    db.execute("insert into outbox values (?,?)", (key,args))
