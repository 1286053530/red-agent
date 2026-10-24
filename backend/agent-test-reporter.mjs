import { resolve } from 'node:path';
// Node's file-only success is not evidence that a behavior was tested.
export default async function* report(source) {
  let passed = 0;
  for await (const { type, data } of source) {
    if (type === 'test:stdout' || type === 'test:stderr') yield data.message;
    if (type === 'test:diagnostic') yield '# ' + data.message + '\n';
    if (type === 'test:pass' || type === 'test:fail') {
      if (type === 'test:pass' && data.file && resolve(data.name) !== resolve(data.file) && data.details?.type === 'test' && !data.skip && !data.todo) passed++;
      yield `${type === 'test:pass' ? 'PASS' : 'FAIL'} ${data.name}\n`;
      if (data.details?.error) yield String(data.details.error.stack || data.details.error.message || data.details.error) + '\n';
    }
    if (type === 'test:summary' && !data.file) yield 'SHUJIN_TEST_EVIDENCE ' + JSON.stringify({ passed }) + '\n';
  }
}
