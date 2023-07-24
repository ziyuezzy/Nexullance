def calculate_average_path_distribution(path_dict):
    # input is a path dictionary
    average_path_length_dict={}
    for sd, paths in path_dict.items():
        average_length=0
        for path in paths:
            average_length+=(len(path)-1)
        average_length/=len(paths)
        average_path_length_dict[sd]=average_length
    # Calculate the average path length of all s-d pairs, 
    # The output is a dictionary of average path lengths
    return average_path_length_dict

#slimfly configurations:
# sf_configs= [722]
sf_configs= [722, 1058]
#jellyfish configurations:
jf_configs =  [(722, 28), (800,31), (900,32), (1058, 34)]
#GDBG configurations, the degree is doubled because it is a directed graph: 
gdbg_configs = [(722, 28*2), (800,31*2), (900,32*2), (1058, 34*2)]
#Equality configurations:
eq_configs= [ # Note that E443 config is fault on the equality paper, so here it is commented out
# (800, 31, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E443"),
(900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
(1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")
]