import os
import tempfile

from colony.node import Graph, PersistentNode


def generate_data(model_params):
    data = '<Generated Data model_params="%s">'%str(model_params)
    return data


def train_model(initial_params, data=None):
    result = 'fitted_params(initial_params=%s, data=%s)' % (initial_params, data)
    return result


def remember_data(new_data, current_data=None):
    current_data = current_data or []
    current_data.append(new_data)
    return current_data


class QTrainer(Graph):

    def __init__(self):
        super(QTrainer, self).__init__()

        self.generate_data = self.add_process_node(target_func = generate_data)

        self.store_data = self.add(PersistentNode,
                                   target_func=remember_data,
                                   name='data',
                                   node_args=(self.generate_data,)
                                   )

        print('store data initialised with %s'%str(self.store_data.get_value()))

        # Connect
        self.store_data.output_port.register_observer(
            self.store_data.passive_input_ports['current_data']
        )

        self.train_model = self.add_process_node(target_func=train_model,
                                                 node_kwargs={'data':self.generate_data})
        self.train_model.output_port.register_observer(
            self.generate_data.reactive_input_ports[0]
        )

if __name__=='__main__':

    trainer = QTrainer()
    trainer.start()

    trainer.generate_data.notify()
    trainer.generate_data.worker.join()

    print('Generated data is %s' % trainer.generate_data.get_value())

    trainer.train_model.notify()
    trainer.train_model.worker.join()

    fitted_params = trainer.train_model.get_value()
    print('Trained model results: %s' % str(fitted_params))

    trainer.train_model.notify(fitted_params)
    trainer.train_model.worker.join()

    print('Trained model results: %s' % str(trainer.train_model.get_value()))

    print('Store data is %s'%str(trainer.store_data.get_value()))
    trainer.generate_data.notify()
    trainer.generate_data.worker.join()

    data = trainer.store_data.get_value()
    print('Store data (len %i) is %s'%(len(data), str(data)))

    # from colony.visualiser import display_colony_graph
    # display_colony_graph(trainer)