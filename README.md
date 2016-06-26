# AirSpider

This is a project combined with three parts to research how to predict the air flights' price change.

# Part I: Spider
Based on urllib2 and some other functions, my own simple spider could fetch data from ceair.com.
## WARNING: This part was valid in 2013 but not sure still valid today.

# Part II: Plot UI
Using matplotlib and wx, I built a UI to see how price of different places and time changed. Then identify some basic pattern in the changes to help build a model.

# Part III: Decision Tree
Each price record has some parameters, and I believe decision tree can help me understand what role played by each parameter in the model. According to parameters given, the trained decision tree will generate a result: "buy" or "wait".
