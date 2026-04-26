/**
 * Application Layer - Use case implementations.
 *
 * This layer orchestrates domain logic.
 * It depends on domain ports (interfaces), NOT on adapters.
 *
 * Following Hexagonal Architecture:
 * - application/ depends on domain/ (ONLY)
 * - Uses domain ports to interact with infrastructure
 * - Contains use case implementations
 */

export * from './use-cases';
