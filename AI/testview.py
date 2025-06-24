import numpy as np
from random import uniform
import math
import pickle
from torch import nn
from torch.masked import masked_tensor
import torch
from bot import NeuralNetwork, inodes, onodes
from dataset import PositionDataset
from torch.utils.data import DataLoader

def training(generation, learnRate):
    training_data = PositionDataset("./trainingData")
    loader = DataLoader(training_data, batch_size=1, shuffle=True)
    model = NeuralNetwork().to("cpu")
    model.load_state_dict(torch.load("./botModels/gen" + str(generation) + ".bot"))
    model.eval()
    n_epochs = 1
    for i in range(5):
        #gamePos, train_MCTS, mask, train_result = next(iter(loader))
        data_file = open("./trainingData/pos" + str(i) + ".pickle", "rb")
        posData = pickle.load(data_file)
        data_file.close()
        #gamePos.requires_grad = True
        #NNpred, NNvaluation = model(gamePos)
        print(posData)
        #print(train_MCTS)
        #print(train_result)
        #myCoolTensor = torch.where(mask, NNpred, float('-inf'))
        #predictedOutput = nn.Softmax(dim=1)(myCoolTensor)
        #loss = AZLossFcn(predictedOutput, train_MCTS, NNvaluation, train_result.float())
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learnRate)
        #optimizer.zero_grad()
        #loss.backward()
        #optimizer.step()

#    torch.save(model.state_dict(), "./AI/botModels/gen" + str(generation+1) + ".bot")

training(0, 0.2)
