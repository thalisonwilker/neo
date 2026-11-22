import { describe, expect, it, vi } from 'vitest';

import { fetchMe, submitPrimeiroAcesso, type ResultadoMe, type UsuarioDTO } from '@/lib/api';
import { DASHBOARD_ROOT_PATH, resolverAcaoDeRota } from './routing';
import {
  lerBoasVindasPendentes,
  limparBoasVindasPendentes,
  marcarBoasVindasPendentes
} from './welcome-state';

const usuarioPendente: UsuarioDTO = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: null,
  primeiro_acesso_concluido: false,
  espacos: []
};

const usuarioConcluido: UsuarioDTO = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: 'Thalyson',
  primeiro_acesso_concluido: true,
  espacos: [{ id: 'e1', nome: 'Neo', tipo: 'trabalho', criado_em: '2026-11-22T12:00:00Z' }]
};

const okPendente: ResultadoMe = { ok: true, status: 200, usuario: usuarioPendente };
const okConcluido: ResultadoMe = { ok: true, status: 200, usuario: usuarioConcluido };

describe('AC-11: matriz de decisão de direcionamento no painel', () => {
  it('AC-11: 200 pendente em /dashboard/* redireciona para /primeiro-acesso', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okPendente,
        pathname: '/dashboard/overview',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'redirecionar', destino: '/primeiro-acesso' });
  });

  it('AC-11 / AC-12: 200 pendente em /primeiro-acesso permite o formulário', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okPendente,
        pathname: '/primeiro-acesso',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'permitir' });
  });

  it('AC-11: 200 pendente em /boas-vindas redireciona para /primeiro-acesso', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okPendente,
        pathname: '/boas-vindas',
        boasVindasPendentes: true
      })
    ).toEqual({ tipo: 'redirecionar', destino: '/primeiro-acesso' });
  });

  it('AC-11: 200 concluído em /dashboard/* permite a rota pedida', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okConcluido,
        pathname: '/dashboard/kanban',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'permitir' });
  });

  it('AC-11: 200 concluído em /primeiro-acesso redireciona para /dashboard', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okConcluido,
        pathname: '/primeiro-acesso',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'redirecionar', destino: DASHBOARD_ROOT_PATH });
  });

  it('AC-11 / AC-13: 200 concluído em /boas-vindas com visita pendente mostra Boas-vindas', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okConcluido,
        pathname: '/boas-vindas',
        boasVindasPendentes: true
      })
    ).toEqual({ tipo: 'permitir' });
  });

  it('AC-11 / AC-13: 200 concluído em /boas-vindas sem visita pendente vai direto para /dashboard', () => {
    expect(
      resolverAcaoDeRota({
        resultadoMe: okConcluido,
        pathname: '/boas-vindas',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'redirecionar', destino: DASHBOARD_ROOT_PATH });
  });

  it('AC-11 / AC-14: 403 em qualquer rota protegida mostra Acesso não liberado', () => {
    const r403: ResultadoMe = {
      ok: false,
      status: 403,
      erro: { erro: 'acesso_nao_liberado', mensagem: 'Não autorizado' }
    };
    expect(
      resolverAcaoDeRota({
        resultadoMe: r403,
        pathname: '/dashboard/overview',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'acesso_nao_liberado' });
  });

  it('AC-11: 401 em qualquer rota protegida encerra sessão e volta para /auth/sign-in', () => {
    const r401: ResultadoMe = {
      ok: false,
      status: 401,
      erro: { erro: 'token_invalido', mensagem: 'Token inválido' }
    };
    expect(
      resolverAcaoDeRota({
        resultadoMe: r401,
        pathname: '/dashboard/overview',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'encerrar_sessao' });
  });

  it('AC-11 / AC-15: 5xx em qualquer rota protegida mostra API indisponível', () => {
    const r503: ResultadoMe = {
      ok: false,
      status: 503,
      erro: { erro: 'api_indisponivel', mensagem: 'Indisponível' }
    };
    expect(
      resolverAcaoDeRota({
        resultadoMe: r503,
        pathname: '/dashboard/overview',
        boasVindasPendentes: false
      })
    ).toEqual({ tipo: 'api_indisponivel' });
  });
});

describe('AC-11: cliente da API Neo (fetchMe e submitPrimeiroAcesso)', () => {
  it('AC-11: fetchMe trata 200, 401, 403, 500 e falha de rede enviando Bearer token', async () => {
    const mockFetch = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify(usuarioPendente), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        })
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ erro: 'acesso_nao_liberado', mensagem: 'Bloqueado' }), {
          status: 403
        })
      )
      .mockResolvedValueOnce(new Response('erro', { status: 500 }))
      .mockRejectedValueOnce(new TypeError('network down'));

    const res200 = await fetchMe('tok_123', mockFetch);
    expect(res200).toEqual({ ok: true, status: 200, usuario: usuarioPendente });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/v1\/me$/),
      expect.objectContaining({
        headers: { Authorization: 'Bearer tok_123' }
      })
    );

    const res403 = await fetchMe('tok_123', mockFetch);
    expect(res403).toMatchObject({ ok: false, status: 403 });

    const res500 = await fetchMe('tok_123', mockFetch);
    expect(res500).toMatchObject({ ok: false, status: 500 });

    const resNet = await fetchMe('tok_123', mockFetch);
    expect(resNet).toMatchObject({ ok: false, status: 503 });

    const resSemToken = await fetchMe(null, mockFetch);
    expect(resSemToken).toMatchObject({ ok: false, status: 401 });
  });

  it('AC-11: submitPrimeiroAcesso trata 201, 422 com campo, 409 e erro de rede', async () => {
    const payload = {
      nome_exibicao: 'Thalyson',
      espaco: { nome: 'Neo', tipo: 'trabalho' as const }
    };
    const mockFetch = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(new Response(JSON.stringify(usuarioConcluido), { status: 201 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            erro: 'dados_invalidos',
            mensagem: 'Nome muito longo',
            campo: 'nome_exibicao'
          }),
          { status: 422 }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ erro: 'primeiro_acesso_ja_concluido', mensagem: 'Já concluído' }),
          { status: 409 }
        )
      )
      .mockRejectedValueOnce(new Error('offline'));

    expect(await submitPrimeiroAcesso('tok', payload, mockFetch)).toEqual({
      ok: true,
      status: 201,
      usuario: usuarioConcluido
    });
    expect(await submitPrimeiroAcesso('tok', payload, mockFetch)).toEqual({
      ok: false,
      status: 422,
      erro: { erro: 'dados_invalidos', mensagem: 'Nome muito longo', campo: 'nome_exibicao' }
    });
    expect(await submitPrimeiroAcesso('tok', payload, mockFetch)).toMatchObject({
      ok: false,
      status: 409
    });
    expect(await submitPrimeiroAcesso('tok', payload, mockFetch)).toMatchObject({
      ok: false,
      status: 503
    });
  });

  it('AC-11: estado em memória de boas-vindas marca, lê e limpa corretamente', () => {
    limparBoasVindasPendentes();
    expect(lerBoasVindasPendentes()).toBeNull();
    marcarBoasVindasPendentes({ nomeExibicao: 'Thalyson', nomeEspaco: 'Neo' });
    expect(lerBoasVindasPendentes()).toEqual({ nomeExibicao: 'Thalyson', nomeEspaco: 'Neo' });
    limparBoasVindasPendentes();
    expect(lerBoasVindasPendentes()).toBeNull();
  });
});
