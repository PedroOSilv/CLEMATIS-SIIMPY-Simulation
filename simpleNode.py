class simpleNode:

    #this class was made just for model the metadata of each node and insert it into a json file
    def __init__(self, timeActivity, activityId, bufferSize, productionStep):
        self.timeActivity = timeActivity
        self.activityId = activityId
        self.bufferSize = bufferSize
        self.productionStep = productionStep