'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Sep 27, 2014

@author: Austin
'''
import pybrain
import pybrain.datasets as datasets
import pybrain.supervised.trainers as trainers

network = pybrain.FeedForwardNetwork()

def Train(epocs, processNum):
    Dataset = datasets.SupervisedDataSet(10, 3)
    Dataset.addSample([0, 0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 1, 0])
    Dataset.addSample([1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0])
    Dataset.addSample([0, 0, 0, 0, 0, 0, 1, 1, 1, 1], [0, 0, 1])
    Dataset.addSample([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], [1, 0, 0])
    Dataset.addSample([0, 0, 1, 1, 1, 1, 1, 1, 0, 0], [0, 1, 0])
    Dataset.addSample([0, 0, 0, 1, 1, 1, 1, 1, 1, 1], [0, 0, 1])
    Dataset.addSample([0, 0, 0, 1, 1, 0, 1, 1, 1, 0], [0, 1, 0])
    
    inLayer = pybrain.LinearLayer(10)
    hiddenLayer = pybrain.SigmoidLayer(20)
    outLayer = pybrain.SoftmaxLayer(3) #Softmax gives probabilities
    
    network.addInputModule(inLayer)
    network.addModule(hiddenLayer)
    network.addOutputModule(outLayer)
    
    in_to_hidden = pybrain.FullConnection(inLayer, hiddenLayer)
    hidden_to_out = pybrain.FullConnection(hiddenLayer, outLayer)
    network.addConnection(in_to_hidden)
    network.addConnection(hidden_to_out)
    
    network.sortModules()
    
    T = trainers.BackpropTrainer(network, learningrate = 0.1, momentum = 0.9)
    #print 'Error Before:', T.testOnData(Dataset, True)
    T.trainOnDataset(Dataset, epocs)
    #print '\nError After:', T.testOnData(Dataset, True)
    

if __name__ == "__main__":
    jobs = []
        
    Train(1000, 0)
    
    print 'Results:', network.activate([0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
    print 'Results:', network.activate([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    print 'Results:', network.activate([1, 1, 1, 0, 1, 0, 0, 0, 0, 0])
    
    