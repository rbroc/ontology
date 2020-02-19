import json
import pandas as pd
import itertools

# Read in json file
j_file = 'ontology.json'
with open(j_file) as jf:
    j_dict = json.load(jf)
j_df = pd.DataFrame(j_dict)

# add parent id columns
j_df['parent_ids'] = 'n/a'
for index, row in j_df.iterrows():
    if row['child_ids'] != []:
        for id in row['child_ids']:
            if j_df['parent_ids'][j_df['id'] == id].item() == 'n/a':
                j_df['parent_ids'][j_df['id'] == id] = row['id']
            else:
                j_df['parent_ids'][j_df['id'] == id] = ' '.join([j_df['parent_ids'][j_df['id'] == id].item(), row['id']])

# Check first level
j_df['levels'] = '0'
j_df['levels'][j_df['parent_ids'] == 'n/a'] = '1'

# Add second level
first_level_id = j_df['id'][j_df['levels'] == '1'].tolist()
j_df['levels'][j_df['parent_ids'].isin(first_level_id)] = '2'

# Add further levels
for i in range(2,7):
    idx = str(i)
    level_id = j_df['id'][j_df['levels'] == idx].tolist()
    for index, row in j_df.iterrows():
        parents = row['parent_ids'].split()
        if any([p in level_id for p in parents]):
            if row['levels'] == '0':
                row['levels'] = str(i + 1)
            else:
                row['levels'] = ' '.join([row['levels'], str(i + 1)])

# Sort levels by parent_id order
j_df['levels_parent_ids'] = 'n/a'
for index, row in j_df.iterrows():
    p_ids = row['parent_ids']
    p_levels = [] 
    parent_map_ids = []
    if p_ids != 'n/a':
        p_ids = p_ids.split()
        for p in p_ids:
            p_lev = j_df['levels'][j_df['id'] == p].item()
            p_lev = [str(int(l) + 1) for l in p_lev.split()]
            p_levels.append(p_lev)
            parent_map_ids.append([p] * len(p_lev))
        flat_levels = list(itertools.chain.from_iterable(p_levels))
        flat_parent_map = list(itertools.chain.from_iterable(parent_map_ids))
        if len(flat_levels) != len(flat_parent_map):
            print(flat_levels)
            print(flat_parent_map)
        row['levels'] = ' '.join(flat_levels)
        row['levels_parent_ids'] = ' '.join(flat_parent_map)

# Convert parent_id and levels to list 
for col in ['parent_ids', 'levels', 'levels_parent_ids']:
    j_df[col] = j_df[col].apply(lambda x: x.split())

# Store both as df and as dict
j_df.to_csv('ontology_df_with_levels.txt', sep='\t')
j_as_dict = [j_df.to_dict(orient='records')]
json.dump(j_as_dict, open('ontology_with_levels.json',"w"))