import torch
import torch.optim as optim
from collections import OrderedDict

t_c = [0.5, 14.0, 15.0, 28.0, 11.0, 8.0, 3.0, -4.0, 6.0, 13.0, 21.0]
t_u = [35.7, 55.9, 58.2, 81.9, 56.3, 48.9, 33.9, 21.8, 48.4, 60.4, 68.4]
t_c = torch.tensor(t_c)
t_u = torch.tensor(t_u)
t_un = t_u * 0.1
w = torch.ones(())
b = torch.zeros(())

import torch.nn as nn

t_c2 = [0.5, 14.0, 15.0, 28.0, 11.0, 8.0, 3.0, -4.0, 6.0, 13.0, 21.0]
t_u2 = [35.7, 55.9, 58.2, 81.9, 56.3, 48.9, 33.9, 21.8, 48.4, 60.4, 68.4]
t_c2 = torch.tensor(t_c2).unsqueeze(1)
t_u2 = torch.tensor(t_u2).unsqueeze(1)

def split(t_c2,t_u2):
    n_samples = t_u2.shape[0]
    n_val = int(0.2 * n_samples)
    shuffled_indices = torch.randperm(n_samples)
    train_indices = shuffled_indices[:-n_val]
    val_indices = shuffled_indices[-n_val:]
    train_indices, val_indices
    train_t_u2 = t_u2[train_indices]
    train_t_c2 = t_c2[train_indices]
    val_t_u2 = t_u2[val_indices]
    val_t_c2 = t_c2[val_indices]
    train_t_un2 = 0.1 * train_t_u2
    val_t_un2 = 0.1 * val_t_u2

    return val_t_un2,train_t_un2,val_t_c2,train_t_c2

t_un_val,t_un_train,t_c_val,t_c_train=split(t_c2,t_u2)


def dloss_fn(t_p, t_c):
    dsq_diffs = 2 * (t_p - t_c) / t_p.size(0)
    return dsq_diffs

def model(t_u, w, b):
    return w * t_u + b

def loss_fn(t_p, t_c):
    squared_diffs = (t_p - t_c)**2
    return squared_diffs.mean()

def dmodel_dw(t_u, w, b):
    return t_u

def dmodel_db(t_u, w, b):
    return 1.0

def grad_fn(t_u, t_c, t_p, w, b):
    dloss_dtp = dloss_fn(t_p, t_c)
    dloss_dw = dloss_dtp * dmodel_dw(t_u, w, b)
    dloss_db = dloss_dtp * dmodel_db(t_u, w, b)
    return torch.stack([dloss_dw.sum(), dloss_db.sum()])

def training_loop(n_epochs, learning_rate, params, t_u, t_c):
    for epoch in range(1, n_epochs + 1):
        w, b = params
        t_p = model(t_u, w, b)
        loss = loss_fn(t_p, t_c)
        grad = grad_fn(t_u, t_c, t_p, w, b)
        params = params - learning_rate * grad
        print('Epoch %d, Loss %f' % (epoch, float(loss)))
    return params

def training_loop2(n_epochs, learning_rate, params, t_u, t_c):
    for epoch in range(1, n_epochs + 1):
        if params.grad is not None:
            params.grad.zero_()

        t_p = model(t_u, *params)
        loss = loss_fn(t_p, t_c)
        loss.backward()
        
        with torch.no_grad():
            params -= learning_rate * params.grad
        if epoch % 500 == 0:
            print('Epoch %d, Loss %f' % (epoch, float(loss)))
    return params

def training_loop3(n_epochs, optimizer, model, loss_fn, t_u_train, t_u_val,t_c_train, t_c_val):
    for epoch in range(1, n_epochs + 1):
        t_p_train = model(t_u_train)
        loss_train = loss_fn(t_p_train, t_c_train)
        t_p_val = model(t_u_val)
        loss_val = loss_fn(t_p_val, t_c_val)
        optimizer.zero_grad()
        loss_train.backward()
        optimizer.step()
        if epoch == 1 or epoch % 1000 == 0:
            print(f"Epoch {epoch}, Training loss {loss_train.item():.4f},"f" Validation loss {loss_val.item():.4f}")

#training_loop2(n_epochs = 5000,learning_rate = 1e-2,params = torch.tensor([1.0, 0.0], requires_grad=True),t_u = t_un,t_c = t_c)
#training_loop(n_epochs = 5000,learning_rate = 1e-2,params = torch.tensor([1.0, 0.0]),t_u = t_un,t_c = t_c)
seq_model = nn.Sequential(OrderedDict([
                            ('hidden_linear', nn.Linear(1, 8)),
                            ('hidden_activation', nn.Tanh()),
                            ('output_linear', nn.Linear(8, 1))
                        ]))

optimizer = optim.SGD(seq_model.parameters(), lr=1e-3)
training_loop3(n_epochs = 5000,optimizer = optimizer,model = seq_model,loss_fn = nn.MSELoss(),t_u_train = t_un_train,t_u_val = t_un_val,t_c_train = t_c_train,t_c_val = t_c_val)

print('output', seq_model(t_un_val))
print('answer', t_c_val)
print('hidden', seq_model.hidden_linear.weight.grad)