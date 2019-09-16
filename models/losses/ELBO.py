import torch
import torch.nn as nn

from models.GeneralModel import GeneralModel


# this is a dummy, please make your own versions that inherets from general model and implements forward

class ELBO(GeneralModel):

    def __init__(self, device="cpu", **kwargs):
        super(ELBO, self).__init__(0, device, **kwargs)

    def forward(self, _, mean, std, reconstructed_mean, x):  # todo: revisit
        """
        calculates negated-ELBO loss
        """

        # todo: revisit

        # regularisation loss
        loss_reg = -0.5 * torch.sum(std - mean.pow(2) - std.exp() + 1, 1).mean()

        # torch.sum(torch.sum(-1 * torch.log(std + 1e-7) + ((std.pow(2) + mean.pow(2)) - 1) * 0.5, dim=1),#                  dim=0)

        # reconstruction loss
        loss_recon = nn.MSELoss(reduction="mean")(reconstructed_mean, x)

        # average over batch size
        return (loss_recon + loss_reg)  # / batch_size