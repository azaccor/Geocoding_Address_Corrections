
# coding: utf-8

# ## How Far Away are these Address Corrections?
# In this short program, we make a call to Google Maps's API using a key from my GCP account. Next, we index the resulting JSON strings to extract the distance we're interested in, define a small function to convert this to a float, and apply it to the existing df. Finally, we make a couple basic visualizations to understand how big of an impact these address corrections have in terms of distance, both based on street address corrections and postal code corrections.  

# In[2]:

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
import requests
import json
import googlemaps ## You may need to pip install this again!


# In[54]:

df = pd.read_excel("Canadian Address Corrections.xlsx")
df.dropna(subset=['NewAddress1'], inplace=True)
## Just take non-matching rows
df = df.loc[df['PostalMatch']==0]
##sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')


# In[55]:

newAddress = (df['NewAddress1'] + ', ' + df['NewCity'] + ', ' + df['NewProv'] + ', Canada')
oldAddress = (df['OldAddress1'] + ', ' + df['OldCity'] + ', ' + df['OldProv'] + ', Canada')
newPostals = (df['NewPostal'] + ', Canada')
oldPostals = (df['OldPostal'] + ', Canada')


# In[56]:

## YOU WILL NEED TO GET A GCP ACCOUNT FOR THIS
gmaps = googlemaps.Client(key='You will need to acquire your own, srry')


# In[57]:

##Based on Address
dist = gmaps.distance_matrix(newAddress[0], oldAddress[0])
dist['rows'][0]['elements'][0]['distance']['text']


# In[58]:

##Based on Postal Code
dist2 = gmaps.distance_matrix(newPostals[0], oldPostals[0])
dist2['rows'][0]['elements'][0]['distance']['text']


# In[59]:

## Based on Address
distances = []
for i in range(0,len(newAddress)):
    result_str = gmaps.distance_matrix(newAddress[i], oldAddress[i])
    new_dist = result_str['rows'][0]['elements'][0]['distance']['text']
    distances.append(new_dist)


# In[60]:

## Based on Postal Codes
distances2 = []
for i in range(0,len(newPostals)):
    try:
        result_str = gmaps.distance_matrix(newPostals[i], oldPostals[i])
        new_dist = result_str['rows'][0]['elements'][0]['distance']['text']
        distances2.append(new_dist)
    except:
        distances2.append("Error")


# In[ ]:

dist2 = gmaps.distance_matrix(newPostals[7], oldPostals[7])
dist2['rows'][0]['elements'][0]['distance']['text']

##V8E 0C6 and T2T 6T4 do not appear to be real. In both cases, these are the "suggested" Postal Codes


# In[61]:

df2 = pd.DataFrame(list(zip(distances, distances2)), columns=['AddDists', 'PostDists'])


# In[62]:

df = pd.concat([df, df2], axis=1)
df.head()


# In[70]:

## Want to convert strings to numbers so we can plot them
def str_to_float(val):
    if 'k' in val:
        val = float(val.split(' ')[0])*1000
    elif ' m' in val:
        val = float(val.split(' ')[0])
    else:
        val = 0
    return val


# In[ ]:

# Apply our new function
df['PostDists'] = df['PostDists'].apply(str_to_float)
df['AddDists'] = df['AddDists'].apply(str_to_float)


# In[81]:

df.head()


# In[95]:

## Basic histogram for address based changes
plt.figure(figsize=(10,5))
plt.xlabel('Distance in Meters')
plt.ylabel('Frequency of Discrepancy')
plt.hist(df['AddDists'], bins = 10)
plt.show()


# In[94]:

## Basic histogram for postal code based changes
plt.figure(figsize=(10,5))
plt.xlabel('Distance in Meters')
plt.ylabel('Frequency of Discrepancy')
plt.hist(df['PostDists'], bins = 10)
plt.show()


# In[96]:

##Run if you want an export
df.to_excel("Canadian Address Updates with Distances.xlsx")


# ### In conclusion:
# We can see that there is a big difference in distance between the address as entered by a member and the post office corrected version when we base the changes on postal code as opposed to just the written street address. In some postal code based cases, this difference can be quite large - over 200km even - whereas most are relatively minor. Using street address suggests that the changes are much more minor, and not likely to result in pricing differences. However, being that we use postal code as the input, this may be something worth exploring down the road.
# 
# --This has been some Austin Zaccor code, 7/18/2019.
