import os, torch, sys
from utils.system_utils import setup_directories, save_codebase_of_run
from utils.model_utils import calculate_accuracy
from torch.utils.data import DataLoader
from utils.constants import *
from typing import List, Tuple


class Tester:
    # input: both network models
    # return average loss, acc; etc.

    def __init__(self,
                 model,
                 data_loader_test: DataLoader,
                 model_state_path='',
                 device='cpu'):

        # the saved network as an object
        self.model = model
        self.model_state_path = model_state_path
        self.data_loader_test = data_loader_test
        self.device = device
        self.model.eval()

    def test(self):
        """
         main training function
        """
        # setup data output directories:
        setup_directories()
        # save_codebase_of_run(self.arguments)

        try:
            # loading saved trained weights
            if self.model_state_path:  # because if we are testing a CombinedClassifier the states are already loaded
                self.model.load_state_dict(torch.load(self.model_state_path))

            log = {'final_scores': [], 'combination': {
                'classifier_scores': [], 'vaes_scores': []},
                   'accuracies_per_batch': [],
                   'true_targets': []}
            for i, (batch, targets, lengths) in enumerate(self.data_loader_test):

                accuracy_batch = self._batch_iteration(batch, targets, lengths, log)

                log['accuracies_per_batch'].append(accuracy_batch)
                log['true_targets'].append(targets)
                break
                # if i>2:
                #     break
            # average over all accuracy batches
            # batches_tested = len(results)
            # average_accuracy = torch.mean(results)
            # average_scores = torch.mean(results["acc"])/batches_tested

            # return average_accuracy, average_scores
            return log
        except KeyboardInterrupt as e:
            print(f"Killed by user: {e}")

            return False
        except Exception as e:
            print(e)

            raise e

    def _batch_iteration(self,
                         batch: torch.Tensor,
                         targets: torch.Tensor,
                         lengths: torch.Tensor,
                         log):
        """
        runs forward pass on batch and backward pass if in train_mode
        """

        batch = batch.to(self.device).detach()
        targets = targets.to(self.device).detach()
        lengths = lengths.to(self.device).detach()

        output = self.model.forward(batch, lengths)

        final_scores_per_class = output
        if 'Combined' in type(self.model).__name__:
            final_scores_per_class, (score_classifier, score_elbo) = output
            log['combination']['classifier_scores'].append(score_classifier.detach())
            log['combination']['vaes_scores'].append(score_elbo.detach())

        _, classifications = score_classifier.detach().max(dim=-1)
        accuracy = (targets.eq(classifications)).float().mean().item()

        log['final_scores'].append(final_scores_per_class.detach())
        return accuracy
