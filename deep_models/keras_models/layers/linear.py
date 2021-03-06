# -*- coding:utf-8 -*-

import tensorflow as tf
# from deep_models.layers.utils import reduce_sum

class Linear(tf.keras.layers.Layer):

    def __init__(self, l2_reg=0.0, mode=0, use_bias=True, **kwargs):

        self.l2_reg = l2_reg
        # self.l2_reg = tf.contrib.layers.l2_regularizer(float(l2_reg_linear))
        if mode not in [0, 1, 2]:
            raise ValueError("mode must be 0,1 or 2")
        self.mode = mode
        self.use_bias = use_bias
        super(Linear, self).__init__(**kwargs)

    def build(self, input_shape):
        if self.use_bias:
            self.bias = self.add_weight(name='linear_bias',
                                        shape=(1,),
                                        initializer=tf.keras.initializers.Zeros(),
                                        trainable=True)
        if self.mode == 1:
            self.kernel = self.add_weight(
                'linear_kernel',
                shape=[int(input_shape[-1]), 1],
                initializer=tf.keras.initializers.glorot_normal(),
                regularizer=tf.keras.regularizers.l2(self.l2_reg),
                trainable=True)
        elif self.mode == 2:
            self.kernel = self.add_weight(
                'linear_kernel',
                shape=[int(input_shape[1][-1]), 1],   # [TensorShape([None, 1, 7]), TensorShape([None, 2])]  shape: (2,)
                initializer=tf.keras.initializers.glorot_normal(),
                regularizer=tf.keras.regularizers.l2(self.l2_reg),
                trainable=True)

        super(Linear, self).build(input_shape)  # Be sure to call this somewhere!

    def call(self, inputs, **kwargs):
        if self.mode == 0:
            categorical_input = inputs
            linear_logit = tf.reduce_sum(categorical_input, axis=-1, keepdims=True)
        elif self.mode == 1:
            numeric_input = inputs
            fc = tf.tensordot(numeric_input, self.kernel, axes=(-1, 0))
            linear_logit = fc
        else:
            categorical_input, numeric_input = inputs
            #  (None, featurenums) tensordot (featurenums, 1) --> (None, 1)
            fc = tf.tensordot(numeric_input, self.kernel, axes=(-1, 0))
            # (None, 1, featurenums) reduce_sum --> (None, 1)
            linear_logit = tf.reduce_sum(categorical_input, axis=-1, keepdims= False) + fc
        if self.use_bias:
            linear_logit += self.bias

        return linear_logit

    def compute_output_shape(self, input_shape):
        return (None, 1)

    def compute_mask(self, inputs, mask):
        return None

    def get_config(self, ):
        config = {'mode': self.mode, 'l2_reg': self.l2_reg,'use_bias':self.use_bias}
        base_config = super(Linear, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
