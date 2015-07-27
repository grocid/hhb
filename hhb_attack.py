import random, copy

class Reader:
    
    p = []
    s = []
    y = []
    k = 0
    step = 0
    b = []
    a = []
    correct_count = 0
    count = 0
    
    def __init__(self, length, s, y):
        self.k = length
        self.p = [0]*self.k
        self.s = s
        self.y = y
        
    def receive_b(self, b):
        self.b = b
    
    def send_a(self):
        self.a = [random.randint(0, 1) for x in range(0, self.k)]
        return copy.copy(self.a)
    
    def verify(self, z):
        zp = [self.a[i] & self.p[i] ^ self.b[i] & self.y[i] for i in range(0, self.k)] 
        self.count += 1
        if z == zp:
            self.correct_count += 1
        if self.count == 20:
            if self.correct_count > 18:
                return 2
            else:
                return 1
        return 0
    
    def step_secret(self):
        tau = random.randint(0, 1)
        zeta = [random.randint(0, 1), random.randint(0, 1)]

        # pick random vectors
        c_1 = [random.randint(0, 1) for x in range(0, k)]
        c_2 = [random.randint(0, 1) for x in range(0, k)]
        c_3 = [random.randint(0, 1) for x in range(0, k)]

        # compute error
        lambda_1 = tau
        lambda_2 = zeta[0]
        lambda_3 = zeta[1]

        # compute scalar product
        t_1 = (sum([c_1[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ lambda_1
        t_2 = (sum([c_2[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ lambda_2
        t_3 = (sum([c_3[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ lambda_3
        
        for i in range(self.step, self.k):
            self.p[i] = zeta[tau]
        
        self.step += 1
        
        if (lambda_1 ^ lambda_2 ^ lambda_3) == 0:
            return ((c_3, t_3), (c_1, t_1), (c_2, t_2))
        else:
            return ((c_2, t_2), (c_3, t_3), (c_1, t_1))

class MITM:
    
    reader = Reader
    k = 0
    bit = 0
    
    def __init__(self, length, s, y):
        # we pass arguments on to the reader
        self.k = length
        self.reader = Reader(self.k, s, y)
    def receive_b(self, b):
        b[self.bit] ^= 1
        self.reader.receive_b(b)
    def send_a(self):
        return self.reader.send_a()
    def verify(self, z):
        return self.reader.verify(z)
    def step_secret(self):
        return self.reader.step_secret()
    #def next_bit(self):
        #self.bit += 1

class Tag:
    
    reader = MITM
    p = []
    s = []
    y = []
    k = 0
    step = 0
    b = []
    a = []
    
    def __init__(self, length, s, y):
        self.k = length
        self.p = [0] * self.k
        self.s = s
        self.y = y
        self.reader = MITM(self.k, s, y)
        
    def send_b(self):
        self.b = [random.randint(0, 1) for x in range(0, self.k)]
        self.reader.receive_b(copy.copy(self.b))
    
    def receive_a(self):
        self.a = self.reader.send_a()
        
    def verify(self):
        z = [self.a[i] & self.p[i] ^ self.b[i] & self.y[i] for i in range(0, self.k)]
        return self.reader.verify(z)
    
    def step_secret(self):
        alpha, beta, gamma = self.reader.step_secret()
        
        tau = 0
        zeta = [0]*2
        
        c_1 = alpha[0]
        c_2 = beta[0]
        c_3 = gamma[0]
        
        t_1 = alpha[1]
        t_2 = beta[1]
        t_3 = gamma[1]
        
        # compute scalar product
        lambda_1 = (sum([c_1[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ t_1
        lambda_2 = (sum([c_2[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ t_2
        lambda_3 = (sum([c_3[i]*(self.s[i] ^ self.p[i]) for i in range(0, k)]) % 2) ^ t_3
    
        
        if (lambda_1 ^ lambda_2 ^ lambda_3) == 0:
            tau = lambda_2
            zeta[0] = lambda_3
            zeta[1] = lambda_1
        else:
            tau = lambda_3
            zeta[0] = lambda_1
            zeta[1] = lambda_2

        for i in range(self.step, self.k):
            self.p[i] = zeta[tau]

        self.step += 1
    
    def MITM_next_bit(self):
        self.reader.next_bit()

k = 20
s = [random.randint(0, 1) for x in range(0, k)]
y = [random.randint(0, 1) for x in range(0, k)]
tag = Tag(k, s, y)

print "-------------"
print s
print y
print "-------------"

for i in range(0, k):
    tag.step_secret()


j = 0
for i in range(0, 20):
    tag.send_b()
    tag.receive_a()
    response = tag.verify()
if response == 2:
    print "bit",str(j),"\t= 0"
else:
    print "bit",str(j),"\t= 1"
#tag.MITM_next_bit()