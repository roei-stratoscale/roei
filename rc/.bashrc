# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions

# Daily Tip - configuring your bash prompt

function _update_ps1() {
    export PS1="$(~/powerline-shell.py $? 2> /dev/null)"
}
export PROMPT_COMMAND="_update_ps1; "


#New Kremnitzer prompt:
#function _update_ps1() {
#    export PS1="$(~/powerline-shell.py $? 2> /dev/null)"
#}
#export PROMPT_COMMAND="_update_ps1; "

#my aliases
alias mys="ssh strato@rack02-server05"
alias scpnorth="scp -r /home/roei/work/northbound/build/rpms/* strato@rack02-server05:work/dc/build/bring/northbound/"
alias vimc="vim /home/roei/roei/commands.txt"
#alias sshnode="/home/roei/work/pydonkey/tools/sshnode.py"
alias sshnode="/home/roei/roei/sshnode.py"
alias rootfsmake="make INSTALLER_EXTRA_ARGS=--skipObfuscation"
alias Rununit="STRATO_CONF_DIRECTORY=/etc/stratoscale UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH="py" python ../voodoo-mock/pytest/pytestrunner.py --verbose "
alias fsmosis="osmosis listlabels --objectStores=osmosis.dc1.strato:1010 | grep "
