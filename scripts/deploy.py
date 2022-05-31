from brownie import YearnHarvest, accounts, network, Contract, web3, Wei
from eth_utils import is_checksum_address
import click


def get_address(msg: str, default: str = None) -> str:
    val = click.prompt(msg, default=default)

    # Keep asking user for click.prompt until it passes
    while True:

        if is_checksum_address(val):
            return val
        elif addr := web3.ens.address(val):
            click.echo(f"Found ENS '{val}' [{addr}]")
            return addr

        click.echo(
            f"I'm sorry, but '{val}' is not a checksummed address or valid ENS record"
        )
        # NOTE: Only display default once
        val = click.prompt(msg)


def main():
    print(f"You are using the '{network.show_active()}' network")
    owner = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    print(f"You are using: 'owner' [{owner.address}]")

    publish_source = click.confirm("Verify source on etherscan?")

    yHarvest = YearnHarvest.deploy({"from": owner}, publish_source=publish_source)

    strategy = Contract("0xA9a904B5567b5AFfb6bB334bea2f90F700EB221a")

    strategy.setKeeper(yHarvest.address, {"from": owner})

    # Run every 4 hours at a minimum
    strategy.setMinReportDelay(60 * 60 * 4, {"from": owner})

    # Fund the yHarvest contract
    owner.transfer(yHarvest, "5 ether")

    assert yHarvest.balance() == Wei("5 ether")

    # Create Gelato job
    tx = yHarvest.createKeeperJob()

    tx.info()
