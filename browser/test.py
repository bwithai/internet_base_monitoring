from browser_history.browsers import Chrome


b = Chrome()

# this gives a list of all available profile names
profiles_available = b.profiles(b.history_file)
print(profiles_available)

# use the history_profiles function to get histories
# it needs a list of profile names to use
outputs = b.history_path_profile("Profile 1")

his = outputs.histories

print(his[-1])