## Assumes this is is run from coursemaster.py via execfile(policy.py)
# The separate file is just to pretend to organize the code.

#%s are tag url_name
policyStartNodeFormat = ''',
    "%s/%s": {
'''

policyEndNodeString = "\n    }"

#%s are key and value
policyKeyValFormat = " "*8 + '''"%s": "%s"'''

policyBaseFormat = """{
    "course/2013_Spring": {
        "graceperiod": "1 day 5 hours 59 minutes 59 seconds",
        "start": "2013-02-04T18:01",
	    "end":  "2013-06-23T12:00",
        "display_name": "Introduction to Probability and Statistics",
        "showanswer": "attempted",
        "rerandomize": "never",
        "show_calculator": "Yes",
        "remote_gradebook": {
	    "name" : "STELLAR:/course/18/sp13/18.05",
	    "section" : ""
        },
        "tabs": [ {"type": "courseware"},
                  {"name": "Course Info", "type": "course_info"},
                  {"name": "Discussion", "type": "discussion"},
                  {"name": "Progress", "type": "progress"}
                ],
        "discussion_topics": {
            "General": {
                "sort_key": "A",
                "id": "1805x_Spring2013_General"
            },
            "Feedback": {
                "sort_key": "AA",
                "id": "1805x_Spring2013_Feedback"
            },
            "Troubleshooting": {
                "sort_key": "AB",
                "id": "1805x_Spring2013_Troubleshooting"
            }
        }
    }%(nodepolicies)s
}
"""

# policy utilities
def writepolicyfile(fname, nodelist):
    if fname != kstdout:
        fp = open(fname,"w")
    else:
        fp = sys.stdout

    pols = ""
    for n in nodelist:
        s = makenodepolicystring(n)
        if s == None: #Could just ignore this
            raise Exception("Node has no policy dict")
        pols += s
    
    allnodepol = policyBaseFormat % {'nodepolicies':pols}
    fp.write(allnodepol)
    if fname != kstdout:
        fp.close()

def makenodepolicystring(node):
    if node.policy == None:
        return(None)

    firstkeyvalpair = True
    ret = policyStartNodeFormat % (node.tag, node.url_name)
    for k,v in node.policy.iteritems():
       s =  policyKeyValFormat % (k,v)
       if not firstkeyvalpair:
           ret += ",\n"       
       ret += s
       firstkeyvalpair = False
    ret += policyEndNodeString

    return(ret)

def easterntoutctimestring(easterntime):
    #See pytz documentation
    #convert a eastern date time to a UTC string for policy file.

    #eastern time = list: (year, month, day, hour, minute)
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.utc
    #year-month-dayThour:min
    fmt = "%Y-%m-%dT%H:%M"

    x = datetime(*easterntime)
    y = eastern.localize(x, is_dst=None)
    z = y.astimezone(utc)
    s = z.strftime(fmt)
    return(s)
