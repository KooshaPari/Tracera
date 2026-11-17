// Preserve the existing router names while routing every unsupported mutation
// through the shared typed contract. No project write has been persisted here.
pub(crate) use crate::not_implemented::not_implemented as create_project_stub;
pub(crate) use crate::not_implemented::not_implemented as update_project_stub;
pub(crate) use crate::not_implemented::not_implemented as delete_project_stub;
