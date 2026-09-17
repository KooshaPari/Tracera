//! High-level distillation API with internal state management.

use std::time::Instant;

use super::config::DistillationConfig;
use super::graph_input::GraphSnapshot;
use super::memory::MemoryEntry;
use super::pattern::distill_patterns;

/// High-level distiller that maintains internal state and exposes
/// incremental distillation, query, and pruning operations.
pub struct MemoryDistiller {
    config: DistillationConfig,
    memories: Vec<MemoryEntry>,
    last_distill: Option<Instant>,
    next_id: u64,
}

impl MemoryDistiller {
    /// Create a new distiller with the given configuration.
    pub fn new(config: DistillationConfig) -> Self {
        Self {
            config,
            memories: Vec::new(),
            last_distill: None,
            next_id: 1,
        }
    }

    /// Run a distillation pass on the provided snapshot, merging new
    /// patterns into the existing memory store.
    pub fn distill(&mut self, snapshot: &GraphSnapshot) -> usize {
        if let Some(prev) = self.last_distill {
            if prev.elapsed() < self.config.interval {
                return 0;
            }
        }

        let new_entries = distill_patterns(snapshot, &self.config);
        let mut added = 0;

        for entry in new_entries {
            if let Some(existing) = self
                .memories
                .iter_mut()
                .find(|m| m.pattern == entry.pattern)
            {
                existing.touch();
                for &src in &entry.source_nodes {
                    if !existing.source_nodes.contains(&src) {
                        existing.source_nodes.push(src);
                    }
                }
            } else if self.memories.len() < self.config.max_memory_size {
                let mut entry = entry;
                entry.id = self.next_id;
                self.next_id += 1;
                self.memories.push(entry);
                added += 1;
            }
        }

        self.last_distill = Some(Instant::now());
        added
    }

    /// Return a reference to all current memory entries.
    pub fn get_memories(&self) -> &[MemoryEntry] {
        &self.memories
    }

    /// Find a memory entry by its pattern fingerprint.
    pub fn find_memory(&self, pattern: &str) -> Option<&MemoryEntry> {
        self.memories.iter().find(|m| m.pattern == pattern)
    }

    /// Prune low-confidence entries and apply decay.
    pub fn prune(&mut self) -> usize {
        let before = self.memories.len();

        for mem in &mut self.memories {
            mem.decay(self.config.decay_factor);
        }

        self.memories
            .retain(|m| m.confidence >= self.config.confidence_threshold);
        before - self.memories.len()
    }

    /// Return the total number of stored memories.
    pub fn memory_count(&self) -> usize {
        self.memories.len()
    }

    /// Clear all memories.
    pub fn clear(&mut self) {
        self.memories.clear();
        self.next_id = 1;
    }

    /// Return memories whose confidence exceeds the given threshold.
    pub fn high_confidence(&self, threshold: f64) -> Vec<&MemoryEntry> {
        self.memories
            .iter()
            .filter(|m| m.confidence >= threshold)
            .collect()
    }
}
