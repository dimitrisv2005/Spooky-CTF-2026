import hashlib

p  = 1099511640127
q  = 340282370743387819766807672197819448083
mu = 145131588818725534535896278189401302887
phi = (-2 * pow(mu - 1, -1, q)) % q
inv_mu = pow(mu - 1, -1, q)
g = (739614761553, 87671554642066775345573935247301052006, 85147831812679793672994902968842668105, 71719252422814786229685092573269912498)
Ma = (739614761553, 312134278234991743315140578529310805510, 126369916264124511285906038626254340804, 134610391672392132751140546119763556201)
Mb = (739614761553, 244699321175961590059239024660541174646, 335110553885376877685776857080059519613, 55552870219389410159628089275413443533)
ct = "9915497c4929fceea2ab3cfd06a744ac9ff6d8de290c8911d18b746d885fb3f5508282d2da0adff5fa15"
a = None
b = None
flag = None

def mpow(e):
    return pow(mu, e % p, q)

def mul(x, y):
    a1, b1, c1, d1 = x
    a2, b2, c2, d2 = y
    m2, im2 = mpow(a2), mpow(-a2)
    return ((a1 + a2) % p,
            (b1 * im2 + b2) % q,
            (c1 * im2 + c2) % q,
            (d1 * m2 + d2 + phi * b2 * c1 * im2
             + (b1 * c1 * (m2 - mpow(-2 * a2))
                + (b1 * c2 - b2 * c1) * (mpow(a1 + a2) - im2)) * inv_mu) % q)

def inv(x):
    a, b, c, d = x
    ma = mpow(a)
    dinv = (-d * mpow(-a) + phi * b * c * mpow(2 * a)
            + b * c * (mpow(2 * a) - mpow(-a)) * inv_mu) % q
    return ((-a) % p, (-b * ma) % q, (-c * ma) % q, dinv)

def conj(a, g):
    return mul(mul(inv(a), g), a)

def assoc(x, y, z):
    ax, bx, gx, _ = x; ay, by, gy, _ = y; az, bz, gz, _ = z
    t1 = mpow(ax + ay) * (mpow(az) - 1) * (bx * gy - by * gx)
    t2 = mpow(ay + az) * (mpow(ax) - 1) * (by * gz - bz * gy)
    t3 = mpow(az + ax) * (mpow(ay) - 1) * (bz * gx - bx * gz)
    return (t1 + t2 + t3) * inv_mu % q

def shared_key(a, g, Mb):
    return assoc(a, g, Mb) * mpow(-a[0]) % q

def mask(K, n):
    return hashlib.shake_256(b"loop|" + K.to_bytes(32, "big")).digest(n)

Ma, Mb = conj(a, g), conj(b, g)
K = shared_key(a, g, Mb)
ct = bytes(x ^ y for x, y in zip(flag, mask(K, 42))).hex()