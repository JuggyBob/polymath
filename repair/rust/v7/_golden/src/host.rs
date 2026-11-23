use super::snapshot;
use super::vm::Vm;
use super::compile_source;

pub struct MiniVM {
    pub vm: Vm,
}

impl MiniVM {
    pub fn from_source(source: &str) -> Result<MiniVM, String> {
        let code = compile_source(source)?;
        Ok(MiniVM { vm: Vm::new(code) })
    }

    pub fn run(&mut self) -> Result<String, String> {
        self.vm.run()?;
        Ok(self.vm.output.clone())
    }

    pub fn snapshot(&self) -> Vec<u8> {
        snapshot::snapshot(&self.vm)
    }
}

pub fn restore(bytes: &[u8]) -> Result<MiniVM, String> {
    let vm = snapshot::restore(bytes)?;
    Ok(MiniVM { vm })
}
