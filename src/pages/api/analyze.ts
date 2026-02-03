import type { APIRoute } from 'astro';
import * as cheerio from 'cheerio';

export interface AuditCheck {
    id: string;
    category: 'Machine Access' | 'Knowledge Layer' | 'Entity Graph';
    name: string;
    status: 'pass' | 'fail' | 'warning';
    score: number;
    maxScore: number;
    details: string;
    advice: string;
    fixCode?: string;
    developerPrompt?: string;
    impact: 'High' | 'Medium' | 'Low';
    complexity: 'Easy' | 'Medium' | 'Hard';
}

export interface AuditResult {
    url: string;
    totalScore: number;
    maxScore: number;
    summary: string;
    categoryScores: {
        machine: number;
        knowledge: number;
        graph: number;
    };
    categoryMaxScores: {
        machine: number;
        knowledge: number;
        graph: number;
    };
    checks: AuditCheck[];
}

export const GET: APIRoute = async ({ url: pageUrl }) => {
    const targetUrl = pageUrl.searchParams.get('url');
    if (!targetUrl) {
        return new Response(JSON.stringify({ error: 'URL is required' }), { status: 400 });
    }

    try {
        const results = await analyzeSite(targetUrl);
        return new Response(JSON.stringify(results), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500 });
    }
};

async function analyzeSite(url: string): Promise<AuditResult> {
    const checks: AuditCheck[] = [];
    let target = url.trim();

    if (!target.startsWith('http')) {
        target = (target.includes('localhost') || target.includes('127.0.0.1')) ? 'http://' + target : 'https://' + target;
    }

    let rootUrl = '';
    try {
        const urlObj = new URL(target);
        rootUrl = urlObj.origin;
    } catch (e) {
        throw new Error('Invalid URL format');
    }

    const fetchSafe = async (u: string) => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);
            const res = await fetch(u, {
                signal: controller.signal,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (AEO-Auditor 7.0)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
            });
            clearTimeout(timeoutId);
            return res;
        } catch (e) {
            return null;
        }
    };

    // 1. Robots.txt
    const robotsRes = await fetchSafe(`${rootUrl}/robots.txt`);
    const robotsText = robotsRes && robotsRes.ok ? await robotsRes.text() : null;
    const hasAiRules = robotsText?.toLowerCase().includes('gptbot') || robotsText?.toLowerCase().includes('claudebot');

    if (!robotsText) {
        checks.push({
            id: 'robots-missing', category: 'Machine Access', name: 'AI Bot Permissions', status: 'fail', score: 0, maxScore: 10, impact: 'High', complexity: 'Easy',
            details: 'Protocol not detected: robots.txt is missing from the origin root.',
            advice: 'Deploy a robots.txt file to allow specific AI crawlers like GPTBot and ClaudeBot for enhanced AEO indexation.',
            fixCode: 'User-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /',
            developerPrompt: 'Create a robots.txt allowing GPTBot and ClaudeBot.'
        });
    } else if (!hasAiRules) {
        checks.push({
            id: 'robots-no-ai', category: 'Machine Access', name: 'AI Bot Permissions', status: 'warning', score: 5, maxScore: 10, impact: 'Medium', complexity: 'Easy',
            details: 'Robots.txt found, but it lacks explicit rules for LLM-based crawlers.',
            advice: 'Update your robots.txt to include explicit Allow directives for AI-specific agents to ensure your content is training-ready.',
            fixCode: 'User-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /',
            developerPrompt: 'Update robots.txt for AI agents.'
        });
    } else {
        checks.push({ id: 'robots-pass', category: 'Machine Access', name: 'AI Bot Permissions', status: 'pass', score: 10, maxScore: 10, impact: 'High', complexity: 'Easy', details: 'Healthy permissions for AI agents detected.', advice: 'Site is highly accessible to major AI crawlers.' });
    }

    // 2. Agents.txt
    const agentsRes = await fetchSafe(`${rootUrl}/agents.txt`);
    if (agentsRes && agentsRes.ok) {
        checks.push({ id: 'agents-pass', category: 'Machine Access', name: 'Agents Protocol', status: 'pass', score: 15, maxScore: 15, impact: 'High', complexity: 'Easy', details: 'New-era agents.txt found.', advice: 'Site follows the latest machine-readable permissions standard.' });
    } else {
        checks.push({
            id: 'agents-fail', category: 'Machine Access', name: 'Agents Protocol', status: 'fail', score: 0, maxScore: 15, impact: 'High', complexity: 'Easy',
            details: 'The agents.txt protocol for granular AI control is not active.',
            advice: 'Implement agents.txt to provide clearer indexing instructions to modern Answer Engines.',
            fixCode: 'User-agent: GPTBot\nAllow: /',
            developerPrompt: 'Create an agents.txt file.'
        });
    }

    // 3. HTML / Semantics
    const htmlRes = await fetchSafe(target);
    const html = htmlRes && htmlRes.ok ? await htmlRes.text() : '';
    const $ = cheerio.load(html);

    const h1s = $('h1').length;
    const hasMain = $('main').length > 0;
    const hasArticle = $('article').length > 0;

    if (h1s === 1 && (hasMain || hasArticle)) {
        checks.push({ id: 'semantics-pass', category: 'Entity Graph', name: 'Semantic Graph', status: 'pass', score: 15, maxScore: 15, impact: 'Medium', complexity: 'Medium', details: 'Full semantic layout (H1 + Semantic Tags) detected.', advice: 'Perfect structural hierarchy for RAG systems.' });
    } else {
        checks.push({
            id: 'semantics-fail', category: 'Entity Graph', name: 'Semantic Graph', status: 'fail', score: 5, maxScore: 15, impact: 'Medium', complexity: 'Medium',
            details: `Structural issues: Found ${h1s} H1 tag(s). Semantic containers: ${hasMain || hasArticle ? 'Detected' : 'Missing'}.`,
            advice: 'Ensure exactly one H1 tag and use semantic HTML5 tags like <main> or <article> to frame your core content.',
            developerPrompt: 'Refactor HTML to include exactly one H1 and semantic tags.'
        });
    }

    // 4. Presence / LLMs.txt
    const llmsRes = await fetchSafe(`${rootUrl}/llms.txt`);
    if (llmsRes && llmsRes.ok) {
        checks.push({ id: 'llms-pass', category: 'Knowledge Layer', name: 'LLM Context Layer', status: 'pass', score: 20, maxScore: 20, impact: 'High', complexity: 'Medium', details: 'llms.txt protocol discovered.', advice: 'Site provides clean RAG context for AI agents.' });
    } else {
        checks.push({
            id: 'llms-fail', category: 'Knowledge Layer', name: 'LLM Context Layer', status: 'fail', score: 0, maxScore: 20, impact: 'High', complexity: 'Medium',
            details: 'Standard LLM documentation file (llms.txt) is missing.',
            advice: 'Create an llms.txt file to serve as a markdown API for LLMs, significantly improving answer accuracy.',
            developerPrompt: 'Generate llms.txt context file.'
        });
    }

    // Categories
    const machineChecks = checks.filter(c => c.category === 'Machine Access');
    const knowledgeChecks = checks.filter(c => c.category === 'Knowledge Layer');
    const graphChecks = checks.filter(c => c.category === 'Entity Graph');

    const machineScore = machineChecks.reduce((acc, c) => acc + c.score, 0);
    const machineMax = machineChecks.reduce((acc, c) => acc + c.maxScore, 0);
    const knowledgeScore = knowledgeChecks.reduce((acc, c) => acc + c.score, 0);
    const knowledgeMax = knowledgeChecks.reduce((acc, c) => acc + c.maxScore, 0);
    const graphScore = graphChecks.reduce((acc, c) => acc + c.score, 0);
    const graphMax = graphChecks.reduce((acc, c) => acc + c.maxScore, 0);

    const totalScore = machineScore + knowledgeScore + graphScore;
    const totalMax = machineMax + knowledgeMax + graphMax;

    return {
        url: target,
        totalScore,
        maxScore: totalMax,
        summary: totalScore > (totalMax * 0.8) ? 'Highly Optimized' : (totalScore > (totalMax * 0.5) ? 'Developing' : 'At Risk'),
        categoryScores: { machine: machineScore, knowledge: knowledgeScore, graph: graphScore },
        categoryMaxScores: { machine: machineMax, knowledge: knowledgeMax, graph: graphMax },
        checks
    };
}
