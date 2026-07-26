// Example: compare two FileSystemHandle objects using isSameEntry
// This runs in the browser where File System Access API is available.

async function isSameHandle(handleA, handleB) {
  // Feature-detect the API
  if (!handleA || !handleB) {
    throw new Error('Both handles are required');
  }

  if (typeof handleA.isSameEntry === 'function') {
    try {
      return await handleA.isSameEntry(handleB);
    } catch (err) {
      console.error('isSameEntry threw:', err);
      return false;
    }
  }

  // Fallback: compare name + kind as a best-effort (not reliable)
  // Only use this when you know your app's constraints.
  return handleA.name === handleB.name && handleA.kind === handleB.kind;
}

// Usage example (browser):
// const [h1] = await window.showOpenFilePicker();
// const [h2] = await window.showOpenFilePicker();
// const same = await isSameHandle(h1, h2);
// console.log('Same entry?', same);

export { isSameHandle };
