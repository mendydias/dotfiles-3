-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- Use Wayland's regular clipboard in local sessions without overriding SSH.
if vim.env.SSH_TTY == nil and vim.fn.executable("wl-copy") == 1 then
  vim.opt.clipboard = "unnamedplus"
end
