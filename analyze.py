from pygithub3 import Github

gh = Github()

watchers = gh.repos.watchers.list(user='julialang', repo='julia')
#print watchers.all()
for w in watchers.all(): 
    print "Processing watcher ", w.__str__() 
    #w_repos = gh.repos.get(user=w)
    #for r in w_repos.all(): 
    #    print r 

