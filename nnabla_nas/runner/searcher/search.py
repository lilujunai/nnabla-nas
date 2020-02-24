import os

from ..runner import Runner


class Searcher(Runner):
    r"""Searching the best architecture."""

    def run(self):
        r"""Run the training process."""
        self.callback_on_start()
        self._start_warmup()

        for cur_epoch in range(self.args.epoch):
            self.monitor.reset()
            lr = self.optimizer['train'].get_learning_rate()
            self.monitor.info(f'Running epoch={cur_epoch}\tlr={lr:.5f}\n')

            for i in range(1):  # range(self.one_epoch_train):
                self.train_on_batch()
                self.valid_on_batch()
                if i % (self.args.print_frequency) == 0:
                    self.monitor.display(i)

            self.callback_on_epoch_end()
            self.monitor.write(cur_epoch)

        self.callback_on_finish()
        self.monitor.close()

        return self

    def _start_warmup(self):
        r"""Performs warmup for the model on training."""
        for cur_epoch in range(self.args.warmup):
            self.monitor.reset()

            lr = self.optimizer['warmup'].get_learning_rate()
            self.monitor.info(f'warm-up epoch={cur_epoch}\tlr={lr:.5f}\n')

            for i in range(1):  # range(self.one_epoch_train):
                self.train_on_batch(key='warmup')
                if i % (self.args.print_frequency) == 0:
                    self.monitor.display(i)

    def callback_on_epoch_end(self):
        r"""Calls this after one epoch."""
        if self.comm.rank == 0:
            self.model.save_parameters(
                path=os.path.join(self.args.output_path, 'arch.h5'),
                params=self.model.get_arch_parameters()
            )
        self.monitor.info(self.model.summary() + '\n')

    def callback_on_finish(self):
        r"""Calls this on finishing the training."""
        if self.comm.rank == 0:
            self.model.save_parameters(
                path=os.path.join(self.args.output_path, 'weights.h5'),
                params=self.model.get_net_parameters()
            )

    def callback_on_start(self):
        r"""Calls this on starting the training."""
        pass
