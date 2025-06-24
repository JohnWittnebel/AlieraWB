import numpy as np
from random import uniform
import math
from torch import nn
from torch.masked import masked_tensor
import torch

hiddennodes = 10
inodes = 2891
#inodes=6
onodes = 129
#onodes=7

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(inodes, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, onodes)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        pred, valuation = logits.split(onodes-1,dim=1)
        valuation = nn.Tanh()(valuation)
        #pred = nn.Softmax(dim=1)(pred)
        return pred, valuation

#Saving code
model = NeuralNetwork().to("cpu")
for name, param in model.named_parameters():
    print(f"Layer: {name} | Size: {param.size()} | Values : {param[:2]} \n")
torch.save(model.state_dict(), "./botModels/currbot.bot")

#Mask
#Y = torch.tensor([0.1,-0.1,0.5,-0.2,0.2,-0.3], dtype=torch.float)
#model = NeuralNetwork().to("cpu")
#mask = torch.tensor([0,0,1,0,0,1], dtype=torch.bool)
#mt = masked_tensor(Y,mask)
#print(nn.Softmax(dim=0)(mt))

#Loading code
#model.load_state_dict(torch.load("./botModels/gen1.bot"))
#model.eval()
#for name, param in model.named_parameters():
#    print(f"Layer: {name} | Size: {param.size()} | Values : {param[:2]} \n")

#print(model.parameters())
#Y = torch.tensor([1,0,0,1,1,1], dtype=torch.float)
#Y = torch.tensor(torch.rand(660))
#print(Y)
#logits = model(Y)
#print(logits)

