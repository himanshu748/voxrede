# Protocol decision record — checked September 20, 2026

Primary source: https://www.assemblyai.com/docs/voice-agents/voice-agent-api/events-reference

The current reference requires tool results while reply.done is the latest received event. It identifies tool-call replies as fc-<call_id>, includes reply_id and completed/interrupted status on reply.done, uses reply.audio.data for PCM16 mono 24 kHz output, and requires session.end followed by session.ended for clean teardown.

The bridge queues mock results by reply ID, drains only completed replies, cancels interrupted reply audio and results, and records clean or failed teardown. Missing reply identities fail the trial rather than silently attaching audio to an unrelated reply. Audio send completion proves successful local WebSocket send, not provider receipt or recognition.

A separate AssemblyAI speech-to-speech guide surfaced conflicting advice about immediate tool results. This implementation follows the specific event reference and the user's requested reply-boundary behavior. Nineteen paid bridge attempts were recorded on September 20. The provider emitted resp-prefixed active reply IDs for tool-call replies; routing now uses the observed reply ID before falling back to the documented fc convention. Real retests confirmed tool results after completed replies. Two focused trials still lacked clean shutdown acknowledgement. Bridge 2.1.2 extends the acknowledgement timeout to eight seconds; this last change has offline regression coverage only.
