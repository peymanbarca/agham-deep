from __future__ import division, print_function, absolute_import

import shutil
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
#from read_from_db import read_csi_from_db
from get_v3 import get_csi
import os

#csi=get_csi() #380*1*90
#csi=np.squeeze(csi) #380*90   20 packet from each of 19 Location

#print(csi)
# Import MNIST data
# from tensorflow.examples.tutorials.mnist import input_data
# mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

# Parameters
learning_rate = 0.01
training_epochs = 500
display_step = 50

#


# x1,y1=mnist.train.next_batch(batch_size)
# x1=np.array(x1)
# print(x1.shape)
# y1=np.array(y1)
# print(y1.shape)

# Network Parameters
n_hidden_1 = 30 # 1st layer num features
n_hidden_2 = 20 # 2nd layer num features
n_hidden_3=10
n_hidden_4=5
n_input = 90



if os.path.isdir(os.getcwd()+'/model'):
        shutil.rmtree(os.getcwd()+'/model')
os.mkdir(os.getcwd()+'/model')
for test_i in range(1,18):   #we must create a sesession for each of loc
    os.mkdir(os.getcwd()+'/model/Test'+str(test_i))
    csi = np.squeeze(np.array(get_csi(test_i)))
    # create and train a graph for each point
    for k in range(16): # for each test we have 16 train point in sn2
        os.mkdir(os.getcwd() + '/model/Test' + str(test_i)+'/'+str(k+1))
        # tf Graph input (only pictures)
        X = tf.placeholder("float", [None, n_input])

        weights = {
            'encoder_h1': tf.Variable(tf.random_normal([n_input, n_hidden_1]), name='w1'),
            'encoder_h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2]), name='w2'),
            'encoder_h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3]), name='w3'),
            'encoder_h4': tf.Variable(tf.random_normal([n_hidden_3, n_hidden_4]), name='w4'),

            'decoder_h1': tf.Variable(tf.random_normal([n_hidden_4, n_hidden_3]), name='w5'),
            'decoder_h2': tf.Variable(tf.random_normal([n_hidden_3, n_hidden_2]), name='w6'),
            'decoder_h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_1]), name='w7'),
            'decoder_h4': tf.Variable(tf.random_normal([n_hidden_1, n_input]), name='w8'),
        }

        biases = {
            'encoder_b1': tf.Variable(tf.random_normal([n_hidden_1]), name='b1'),
            'encoder_b2': tf.Variable(tf.random_normal([n_hidden_2]), name='b2'),
            'encoder_b3': tf.Variable(tf.random_normal([n_hidden_3]), name='b3'),
            'encoder_b4': tf.Variable(tf.random_normal([n_hidden_4]), name='b4'),

            'decoder_b1': tf.Variable(tf.random_normal([n_hidden_3]), name='b5'),
            'decoder_b2': tf.Variable(tf.random_normal([n_hidden_2]), name='b6'),
            'decoder_b3': tf.Variable(tf.random_normal([n_hidden_1]), name='b7'),
            'decoder_b4': tf.Variable(tf.random_normal([n_input]), name='b8'),
        }


        # Building the encoder
        def encoder(x):
            # Encoder Hidden layer with sigmoid activation #1
            layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']),
                                           biases['encoder_b1']))
            # Decoder Hidden layer with sigmoid activation #2
            layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']),
                                           biases['encoder_b2']))

            layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['encoder_h3']),
                                           biases['encoder_b3']))

            layer_4 = tf.nn.sigmoid(tf.add(tf.matmul(layer_3, weights['encoder_h4']),
                                           biases['encoder_b4']))
            return layer_4


        # Building the decoder
        def decoder(x):
            # Encoder Hidden layer with sigmoid activation #1
            layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']),
                                           biases['decoder_b1']))
            # Decoder Hidden layer with sigmoid activation #2
            layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']),
                                           biases['decoder_b2']))

            layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['decoder_h3']),
                                           biases['decoder_b3']))

            layer_4 = tf.nn.sigmoid(tf.add(tf.matmul(layer_3, weights['decoder_h4']),
                                           biases['decoder_b4']))
            return layer_4


        # Construct model
        encoder_op = encoder(X)
        decoder_op = decoder(encoder_op)

        # Prediction
        y_pred = decoder_op

        # Targets (Labels) are the input data.
        y_true = X

        # Define loss and optimizer, minimize the squared error
        cost = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
        optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(cost)

        # Initializing the variables
        init = tf.global_variables_initializer()

        saver = tf.train.Saver()
        x=csi[k*15:(k+1)*15,:]
        print(np.array(x).shape)
        # Launch the graph
        with tf.Session() as sess:
            sess.run(init)
            # Training cycle
            for epoch in range(training_epochs):
                # Loop over all batches

                # Run optimization op (backprop) and cost op (to get loss value)
                _, c = sess.run([optimizer, cost], feed_dict={X: x})
                tf.add_to_collection("predict", y_pred)
                # Display logs per epoch step
                if epoch % display_step == 0:
                    print("Epoch:", '%04d' % (epoch+1),"cost=", "{:.9f}".format(c))

            print("Optimization Finished! For test " + str(test_i) +" point " + str(k+1) )
            saver.save(sess,os.path.join(os.getcwd()+'/model/Test'+str(test_i)+'/'+str(k+1), 'trained_variables'+str(test_i)+str(k+1)+'.ckpt'))
        tf.reset_default_graph()