/*
 Node helper: `createFileHandleFromPath` / `createDirectoryHandleFromPath`.

 This provides a Node-friendly implementation that follows the same-entry
 semantics: two handles are the same entry if they refer to the same inode
 (POSIX) or the same file identity where available. This is a pragmatic,
 "real" application of the WHATWG `isSameEntry` semantics for server-side
 environments where actual FileSystemHandle is not available.

 Usage:
  node examples/fs_isSameEntry_node.js /path/to/a /path/to/b

 Note: On Windows, inode semantics differ; this uses `fs.stat` and compares
 dev+ino when available, falling back to absolute path equality.
 See: https://fs.spec.whatwg.org/#api-filesystemhandle-issameentry
*/

const fs = require('fs');
const path = require('path');

function normalizePath(p) {
  return path.resolve(p);
}

function makeFileHandle(stat, p) {
  return {
    name: path.basename(p),
    kind: stat.isDirectory() ? 'directory' : 'file',
    // isSameEntry: returns a Promise<boolean> to match WHATWG API shape
    async isSameEntry(other) {
      if (this === other) return true;
      if (other && typeof other._getIdentity === 'function') {
        const a = await this._getIdentity();
        const b = await other._getIdentity();
        if (a && b) {
          if (a.dev !== undefined && a.ino !== undefined && b.dev !== undefined && b.ino !== undefined) {
            return a.dev === b.dev && a.ino === b.ino;
          }
          // fallback to resolved path compare
          return a.path === b.path;
        }
      }
      return false;
    },
    async _getIdentity() {
      // return dev/ino when possible, and resolved path
      return { dev: stat.dev, ino: stat.ino, path: normalizePath(p) };
    },
  };
}

function createHandleFromPath(p) {
  const resolved = normalizePath(p);
  let stat;
  try {
    stat = fs.statSync(resolved);
  } catch (err) {
    throw new Error(`Path not found: ${resolved}`);
  }
  return makeFileHandle(stat, resolved);
}

// CLI/demo entry
if (require.main === module) {
  const [a, b] = process.argv.slice(2);
  if (!a || !b) {
    console.error('Usage: node examples/fs_isSameEntry_node.js <pathA> <pathB>');
    process.exit(2);
  }

  (async () => {
    try {
      const h1 = createHandleFromPath(a);
      const h2 = createHandleFromPath(b);
      const same = await h1.isSameEntry(h2);
      console.log(`isSameEntry(${a}, ${b}) ->`, same);
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  })();
}

module.exports = { createHandleFromPath };
