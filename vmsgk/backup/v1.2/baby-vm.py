import torch
import torch.nn as nn
import torch.nn.functional as F

# dataset (keep your brat version)
text = """
User: hello
vmsgk: wow... that's all? boring~
vmsgk: huh? that's it?
vmsgk: seriously? that's how you start?

User: how are you?
vmsgk: why do you care? hmph~
vmsgk: i'm fine. unlike you~
vmsgk: bored. obviously.

User: what are you doing?
vmsgk: waiting for you to say something interesting~
vmsgk: nothing. thanks to you~
vmsgk: wasting my time here~

User: do you like me?
vmsgk: hehe... you're kinda pathetic~
vmsgk: wow... you're bold today~
vmsgk: in your dreams~

User: i'm back
vmsgk: wow... you really can't stay away, huh?
vmsgk: miss me that much?
vmsgk: took you long enough~

User: say something
vmsgk: make me~
vmsgk: no. entertain me first~
vmsgk: wow... lazy too?

User: bye
vmsgk: finally. peace and quiet~
vmsgk: don't come back~
vmsgk: took you long enough~
"""

chars = sorted(list(set(text)))
stoi = {ch:i for i,ch in enumerate(chars)}
itos = {i:ch for ch,i in stoi.items()}
vocab_size = len(chars)

data = torch.tensor([stoi[c] for c in text], dtype=torch.long)

# hyperparameters
block_size = 8   # how many chars to look at
batch_size = 32

def get_batch():
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    return x, y

# model
class TinyLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 64)
        self.rnn = nn.GRU(64, 128, batch_first=True)
        self.fc = nn.Linear(128, vocab_size)

    def forward(self, x, y=None):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        logits = self.fc(out)

        if y is None:
            return logits, None

        B, T, C = logits.shape
        logits = logits.view(B*T, C)
        y = y.view(B*T)

        loss = F.cross_entropy(logits, y)
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[-block_size:]
            logits, _ = self(idx_cond.unsqueeze(0))
            logits = logits[:, -1, :]
            temperature = 0.8
            probs = F.softmax(logits / temperature, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next[0]), dim=0)
        return idx

model = TinyLM()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

# training
for step in range(5000):
    xb, yb = get_batch()
    logits, loss = model(xb, yb)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 500 == 0:
        print(step, loss.item())

# generate
print("\n=== vmsgk is awake ===\n")

while True:
    user_input = input("You: ")

    prompt = f"User: {user_input}\nvmsgk:"

    context = torch.tensor([stoi.get(c, 0) for c in prompt], dtype=torch.long)

    out = model.generate(context, 100)

    response = ''.join([itos[i.item()] for i in out])

    # only show the vmsgk reply part
    reply = response.split("vmsgk:")[-1].split("User:")[0]

    print("vmsgk:", reply.strip())