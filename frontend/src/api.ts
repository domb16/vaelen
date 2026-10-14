export async function api(path: string, opts = {}) {
    const res = await fetch(`/api${path}`, {
        credentials: 'include',
        headers: {"Content-Type": 'application/json'},
        ...opts,
    });

    if (res.status === 401){
        window.location.href = '/login';
        throw new Error('unauthenticated');
    }
    return res;
}