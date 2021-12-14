# -*- coding: utf-8 -*-
"""project2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16g1mDvQ1my20_4DZnxE8JiP2I5D4Qv0J
"""

import torch
import sys
import math

"""
Generates a training and a test set of 1, 000 points sampled uniformly in [0, 1] , 
each with a label 0 if outside the disk centered at (0.5, 0.5) of radius 1/ 2π, and 1 inside
"""
def generate_disc_set(nb): 
    input = torch.rand(nb, 2, dtype=torch.float32)
    label = torch.zeros(nb, dtype=torch.int64)
    # input = torch.empty((1000, 2)).normal(mean=0,var)
    dis = 1 / (2 * math.pi)
    for i in range(input.size(0)):
      if ((input[i] - 0.5).square().sum()) < dis:
        # print(i)
        label[i] = 1
      # print(input[i].square().sum())
    # print(label)
    return input, label

def sigmoid(result):
    for idx,layer in enumerate(result):
        result[idx] = 1 / (1 + math.exp(-layer))   
    return result

def sigma(delta, weight, result): # Calculation of hidden layers (Derived from the relationship between the front and back layers)
    sig = torch.zeros(1, weight.size(0) - 1) #except the output layer
    # print('sig_size:', sig.size())
    for neu in range(weight.size(0) - 1):  # Calculate the delta of each neuron one by one 神經元逐一計算相對的delta
        for x in range(weight.size(1)): #for RELU, if result>=0, [sigma = delta*weight] 利用weight的後一位判斷應該要用的維度，判斷原先的輸出是否大於零
            if result[0][x] > 0: 
                sig[0][neu] += (delta[0][x] * weight[neu][x])
    return sig
    # print(weight)

def loss(v, t):
    # print((v - t).pow(2).sum())
    return (v - t).pow(2).sum()

input, label = generate_disc_set(1000)
test_input, test_label = generate_disc_set(1000)

print('input:', input, ' label:', label)

class Module:
    def __init__(self, layer = 3, neuron = 25):
        self.layer = layer
        self.neu = neuron
        self.lr = 0.01
        self.input_shape = 2
        self.output_shape = 1    

    def init_weight(self):
        self.weight = []
        ##for input layer
        self.weight.append(torch.rand(self.input_shape, self.neu) * 2 - 1) #let random number range 0~1 => -1~1
        ##for hidden layer
        for i in range(1, self.layer):
            self.weight.append(torch.rand(self.neu+1, self.neu) * 2 - 1) #input dimension = neu number + 1(bias)
        ##for ouput layer
        self.weight.append(torch.rand(self.neu+1, self.output_shape) * 2 - 1)
        # print('weight:', self.weight)
        # print('weight size:', self.weight[1].size())

    def forward_pass(self, train_data):
        result = []
        ## input layer
        result.append(torch.mm(train_data.expand(1, -1), self.weight[0]).relu())
        result[0] = torch.cat((result[0], torch.tensor([[1]])), 1) #caculate the bias by adding 1 to the first posotion of the result 補1
        ## hidden layers
        for idx in range(1, self.layer): 
            result.append(torch.mm(result[idx - 1], self.weight[idx]).relu())
            result[idx] = torch.cat((result[idx], torch.tensor([[1]])), 1)
        ## output layer
        result.append(sigmoid(torch.mm(result[self.layer-1], self.weight[self.layer]))) #last layer go through sigmoid function

        # print('result:', result)
        return result

    def backward_pass(self, result, target):
        delta = []
        ## output layer 
        delta_temp = (target - result[self.layer]).mul(result[self.layer].mul(1 - result[self.layer]))
        delta.append(delta_temp)

        for k in range(self.layer-1, -1, -1):
            # print('back_lay:', k)
            # print('delta_0:', delta[0])
            # print('weight_size:', self.weight[k + 1].size())
            
            delta_temp = sigma(delta[0], self.weight[k + 1], result[k + 1])
            delta.insert(0, delta_temp) #往前插到第一個位置
            # print('-----')
        return delta

    def modi_weight(self, delta, input, result):
        # print('weight_a:', self.weight[0])
        # print('input:', input)
        # print('delta:', delta[0])
        self.weight[0] += (self.lr * (input.reshape(2, 1).mm(delta[0])))
        for i in range(1, self.layer + 1):
            # print('i:', i)
            # print(delta[i - 1])
            self.weight[i] += (self.lr * (result[i - 1].t().mm(delta[i])))
        # print(self.weight)
        # print('modi_weight:', self.weight)

    def cal_acc(self, data, target):
        right = 0
        for i in range(data.size(0)):
            output = self.forward_pass(data[i])
            if output[-1].round() == target[i]:
              right += 1
        return right
            


epoch = 50

x1 = Module(layer=3, neuron=25)
x1.init_weight()

for r in range(epoch):
    acc_loss = 0
    print('epoch:', r)
    for i in range(len(input)):
        result = x1.forward_pass(input[i])
        acc_loss += loss(label[i], result[-1])
        delta = x1.backward_pass(result, label[i])
        x1.modi_weight(delta, input[i], result)
    print('acc_loss:', acc_loss)
    right = x1.cal_acc(test_input, test_label)
    print('acc:', right/test_input.size(0))
    print('------')