import { describe, expect, it, vi } from 'vitest';

import { criarEspaco } from './neo-client';

const payload = {
  nome: 'Faculdade',
  tipo: 'estudos' as const,
  meta_semanal: 12,
  agentes_sugeridos: true
};

const resposta = (status: number, corpo: unknown) =>
  new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' }
  });

describe('0040 AC-10 e AC-11: cliente criarEspaco', () => {
  it('envia POST /v1/espacos com o token e devolve o Espaço criado', async () => {
    const espaco = { id: 'e2', ...payload, criado_em: '2026-11-22T13:00:00Z' };
    const fetchImpl = vi.fn().mockResolvedValue(resposta(201, espaco));

    const resultado = await criarEspaco('tok', payload, fetchImpl);

    expect(resultado).toEqual({ ok: true, status: 201, espaco });
    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe('http://localhost:8000/v1/espacos');
    expect(init.method).toBe('POST');
    expect(init.headers.Authorization).toBe('Bearer tok');
    expect(JSON.parse(init.body)).toEqual(payload);
  });

  it('422 devolve o campo e a mensagem da API', async () => {
    const erro = { erro: 'dados_invalidos', mensagem: 'Nome inválido.', campo: 'nome' };
    const fetchImpl = vi.fn().mockResolvedValue(resposta(422, erro));
    expect(await criarEspaco('tok', payload, fetchImpl)).toEqual({
      ok: false,
      status: 422,
      erro
    });
  });

  it('falha de rede vira 503 api_indisponivel', async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    const resultado = await criarEspaco('tok', payload, fetchImpl);
    expect(resultado).toMatchObject({ ok: false, status: 503, erro: { erro: 'api_indisponivel' } });
  });

  it('sem token não chama a API', async () => {
    const fetchImpl = vi.fn();
    const resultado = await criarEspaco(null, payload, fetchImpl);
    expect(resultado).toMatchObject({ ok: false, status: 401 });
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});
