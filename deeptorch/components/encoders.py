from ..templates import Node
from ..core import DeepTorchModule
from ..config import Config, Ref

import torch.nn as nn

class Encoder(DeepTorchModule):

    defaults = (
        Config()
        .depth(4)
        .blocks(Node("layer") >> Node("activation") >> Node("pool"))
    )

    def __init__(self, depth=4, blocks=None):
        """Encoder module.
        blocks:
            Default: Node("layer") >> Node("activation") >> Node("pool")
            Specification for the blocks of the encoder.
        depth:
            Default: 4
        """

        super().__init__(depth=depth, blocks=blocks)

        self.depth = self.attr("depth")
        self.blocks = self.create_many("blocks", self.depth)

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return x


class ConvolutionalEncoder(Encoder):
    defaults = (
        Config()
        .merge(None, Encoder.defaults)
        .blocks.populate("layer.out_channels", lambda i: 8 * 2 ** i, length=8)
        .blocks.layer(nn.LazyConv2d, kernel_size=3, padding=1)
        .blocks.activation(nn.ReLU)
        .blocks.pool(nn.MaxPool2d, kernel_size=2)
    )


class DenseEncoder(Encoder):
    defaults = (
        Config()
        .merge(None, Encoder.defaults)
        .blocks.layer(nn.LazyLinear, out_features=128)
        .blocks.activation(nn.ReLU)
        .blocks.pool(nn.Identity)
    )