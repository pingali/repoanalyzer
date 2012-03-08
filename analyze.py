from pygithub3 import Github
import time 
import operator 
import sys

# Debug
debug = True
max_watchers = 1000                 # Max number of watchers to process 
ignore_duplicate_repos = True       # Count each repo only once (ignore forks)

# overall stats
all_repositories = {} 
total_repositories = 0 
total_watchers = 0 

# All languages
language_distribution_raw = {} 
language_count = {} 

# Only the top n languages 
top_n = 5
language_distribution_top_n = {} 
language_count_top_n = {} 

def update_hash(h, k, v): 
    """
    Update the hash 
    """
    if k in h:
        h[k] += v 
    else:
        h[k] = v

def print_hash(h, title, description=""): 
    """
    Structure the output 
    """
    print "=" * len(title)
    print "%s" % (title) 
    print "-" * len(title)
    sorted_h = sorted(h.iteritems(), 
                              key=operator.itemgetter(1), 
                              reverse=True)
    for (k,v) in sorted_h: 
        print "%12s\t%12d" % (k, v) 
    print "=" * len(title)
        
def process_language_dict(watcher_name, repo_name, languages):
    """
    Process the language information available for each watcher and
    repo combination. Languages is a dictionary with tuples(lang ->
    code size)
    """
    global total_repositories, language_distribution_raw 
    global top_n, language_distribution_top_n 
    global debug 

    total_repositories += 1     

    # Count languages 
    for k,v in languages.items(): 
        update_hash(language_count, k, 1) 
        update_hash(language_distribution_raw, k, v) 

    sorted_languages = sorted(languages.iteritems(), 
                              key=operator.itemgetter(1), reverse=True)
    
    count = top_n 
    for (k,v) in sorted_languages: 
        if (v == 0): 
            next 
        update_hash(language_distribution_top_n, k, v) 
        update_hash(language_count_top_n, k, 1) 
        count -= 1 
        if (count <= 0): 
            break 
            

def process(gh, root_user, root_repo): 
    """
    Main function. Looks for the watchers of each repo and for each
    watcher obtain a list of repos and language distribution of each
    repo.
    
    """
    global debug, all_repositories, ignore_duplicate_repos
    global max_watchers, total_watchers, total_repositories

    watchers = gh.repos.watchers.list(user=root_user, repo=root_repo)
    print "# Obtained all watchers" 
    
    for w in watchers.all(): 
        watcher_name = getattr(w, 'login','')
        watcher_name = watcher_name.encode('ascii', 'ignore')
        
        # Ignore self 
        if (watcher_name.lower() == root_user.lower()):
            continue 

        total_watchers += 1 

        try: 
            print "# Processing watcher %d - %s  (completed %d repos) " % \
			(total_watchers, watcher_name, total_repositories)
            repos = gh.repos.list(watcher_name).all() 
            #if debug: print "# ", repos 
            for repo in repos: 
                repo_name = getattr(repo, 'name', '') 
                repo_name = repo_name.encode('ascii', 'ignore') 
                if debug: print "# repo name ", repo_name
                # Ignore duplicates 
                if ignore_duplicate_repos: 
                    if repo_name in all_repositories: 
                        if debug: print "# Duplicate. Ignoring" 
                        continue
                    else:
                        all_repositories[repo_name] = 1 

                try: 
                    languages = gh.repos.list_languages(user=watcher_name, 
                                                        repo=repo_name)
                    if debug: print "# languages ", languages
                    process_language_dict(watcher_name, repo_name, languages)
                except: 
                    if debug: print "# Repo Error %s %s" % (watcher_name, repo_name)
                    pass 
                time.sleep(1)
        except:
            if debug: print "# Watcher %s" % (watcher_name)
            pass 

        if debug: 
            if (total_watchers >= max_watchers): 
                break 


#############################################################
# Main 
#############################################################

if (len(sys.argv) > 2):
    root_user = sys.argv[1]
    root_repo = sys.argv[2]
else:
    print "Usage: python analyze.py <username> <repository>" 
    exit(1) 

if debug: print "# Processing %s/%s " % (root_user, root_repo)  

gh = Github()
process(gh, root_user, root_repo) 

#############################################################
# Output
#############################################################

print "Repo Statistics for %s/%s"  % (root_user, root_repo)
print "-----------------------------" 
print "Command: python analyze.py %s %s " % (root_user, root_repo)
print "Flags: debug = %s, max_watchers = %d, ignore duplicate repos = %s" \
    % (debug, max_watchers, ignore_duplicate_repos) 
print "Total Watchers: %d" % total_watchers 
print "Total Repositories: %d" % total_repositories 
print_hash(language_count, "Repos using Language",   "") 
print_hash(language_distribution_raw, "Code Size Distribution across All Repos", ) 
print_hash(language_count_top_n, "Repos using Language (Top %d langs/Repo)" % top_n, "") 
print_hash(language_distribution_top_n, "Code Size Distribution (Top %d Langs/Repo" % top_n, "") 
