#!/usr/bin/env python

import io
import unittest

from pycoin.tx import Tx, ValidationFailureError, script
from pycoin.tx.script import tools
from pycoin.serialize import h2b, h2b_rev
from pycoin.block import Block

class ValidatingTest(unittest.TestCase):
    def test_validate(self):
        # block 80971
        block_80971_cs = h2b('00000000001126456C67A1F5F0FF0268F53B4F22E0531DC70C7B69746AF69DAC')
        block_80971_data = h2b('01000000950A1631FB9FAC411DFB173487B9E18018B7C6F7147E78C06258410000000000A881352F97F14B'\
        'F191B54915AE124E051B8FE6C3922C5082B34EAD503000FC34D891974CED66471B4016850A040100'\
        '0000010000000000000000000000000000000000000000000000000000000000000000FFFFFFFF080'\
        '4ED66471B02C301FFFFFFFF0100F2052A01000000434104CB6B6B4EADC96C7D08B21B29D0ADA5F29F937'\
        '8978CABDB602B8B65DA08C8A93CAAB46F5ABD59889BAC704925942DD77A2116D10E0274CAD944C71D3D1A'\
        '670570AC0000000001000000018C55ED829F16A4E43902940D3D33005264606D5F7D555B5F67EE4C033390'\
        'C2EB010000008A47304402202D1BF606648EDCDB124C1254930852D99188E1231715031CBEAEA80CCFD2B39A'\
        '02201FA9D6EE7A1763580E342474FC1AEF59B0468F98479953437F525063E25675DE014104A01F763CFBF5E518'\
        'C628939158AF3DC0CAAC35C4BA7BC1CE8B7E634E8CDC44E15F0296B250282BD649BAA8398D199F2424FCDCD88'\
        'D3A9ED186E4FD3CB9BF57CFFFFFFFFF02404B4C00000000001976A9148156FF75BEF24B35ACCE3C05289A241'\
        '1E1B0E57988AC00AA38DF010000001976A914BC7E692A5FFE95A596712F5ED83393B3002E452E88AC000000'\
        '0001000000019C97AFDF6C9A31FFA86D71EA79A079001E2B59EE408FD418498219400639AC0A010000008B4'\
        '830450220363CFFAE09599397B21E6D8A8073FB1DFBE06B6ACDD0F2F7D3FEA86CA9C3F605022100FA255A6ED'\
        '23FD825C759EF1A885A31CAD0989606CA8A3A16657D50FE3CEF5828014104FF444BAC08308B9EC97F56A652A'\
        'D8866E0BA804DA97868909999566CB377F4A2C8F1000E83B496868F3A282E1A34DF78565B65C15C3FA21A076'\
        '3FD81A3DFBBB6FFFFFFFF02C05EECDE010000001976A914588554E6CC64E7343D77117DA7E01357A6111B798'\
        '8AC404B4C00000000001976A914CA6EB218592F289999F13916EE32829AD587DBC588AC00000000010000000'\
        '1BEF5C9225CB9FE3DEF929423FA36AAD9980B9D6F8F3070001ACF3A5FB389A69F000000004A493046022100F'\
        'B23B1E2F2FB8B96E04D220D385346290A9349F89BBBC5C225D5A56D931F8A8E022100F298EB28294B90C1BAF'\
        '319DAB713E7CA721AAADD8FCC15F849DE7B0A6CF5412101FFFFFFFF0100F2052A010000001976A9146DDEA80'\
        '71439951115469D0D2E2B80ECBCDD48DB88AC00000000');

        # block 80974
        block_80974_cs = h2b('0000000000089F7910F6755C10EA2795EC368A29B435D80770AD78493A6FECF1')
        block_80974_data = h2b('010000007480150B299A16BBCE5CCDB1D1BBC65CFC5893B01E6619107C55200000000000790'\
        '0A2B203D24C69710AB6A94BEB937E1B1ADD64C2327E268D8C3E5F8B41DBED8796974CED66471B204C3247030'\
        '1000000010000000000000000000000000000000000000000000000000000000000000000FFFFFFFF0804ED6'\
        '6471B024001FFFFFFFF0100F2052A010000004341045FEE68BAB9915C4EDCA4C680420ED28BBC369ED84D48A'\
        'C178E1F5F7EEAC455BBE270DABA06802145854B5E29F0A7F816E2DF906E0FE4F6D5B4C9B92940E4F0EDAC000'\
        '000000100000001F7B30415D1A7BF6DB91CB2A272767C6799D721A4178AA328E0D77C199CB3B57F010000008'\
        'A4730440220556F61B84F16E637836D2E74B8CB784DE40C28FE3EF93CCB7406504EE9C7CAA5022043BD4749D'\
        '4F3F7F831AC696748AD8D8E79AEB4A1C539E742AA3256910FC88E170141049A414D94345712893A828DE57B4C'\
        '2054E2F596CDCA9D0B4451BA1CA5F8847830B9BE6E196450E6ABB21C540EA31BE310271AA00A49ED0BA930743'\
        'D1ED465BAD0FFFFFFFF0200E1F505000000001976A914529A63393D63E980ACE6FA885C5A89E4F27AA08988AC'\
        'C0ADA41A000000001976A9145D17976537F308865ED533CCCFDD76558CA3C8F088AC000000000100000001651'\
        '48D894D3922EF5FFDA962BE26016635C933D470C8B0AB7618E869E3F70E3C000000008B48304502207F5779EB'\
        'F4834FEAEFF4D250898324EB5C0833B16D7AF4C1CB0F66F50FCF6E85022100B78A65377FD018281E77285EFC3'\
        '1E5B9BA7CB7E20E015CF6B7FA3E4A466DD195014104072AD79E0AA38C05FA33DD185F84C17F611E58A8658CE'\
        '996D8B04395B99C7BE36529CAB7606900A0CD5A7AEBC6B233EA8E0FE60943054C63620E05E5B85F0426FFFFF'\
        'FFF02404B4C00000000001976A914D4CAA8447532CA8EE4C80A1AE1D230A01E22BFDB88AC8013A0DE0100000'\
        '01976A9149661A79AE1F6D487AF3420C13E649D6DF3747FC288AC00000000')

        block_80971 = Block.parse(io.BytesIO(block_80971_data))
        block_80974 = Block.parse(io.BytesIO(block_80974_data))

        tx_db = dict((tx.hash(), tx) for tx in block_80971.txs)

        tx_to_validate = block_80974.txs[2]
        self.assertEqual("OP_DUP OP_HASH160 d4caa8447532ca8ee4c80a1ae1d230a01e22bfdb OP_EQUALVERIFY OP_CHECKSIG",
            tools.disassemble(tx_to_validate.txs_out[0].script))
        self.assertEqual(tx_to_validate.hash(), h2b_rev("7c4f5385050c18aa8df2ba50da566bbab68635999cc99b75124863da1594195b"))

        tx_to_validate.validate(tx_db)

        # now, let's corrupt the Tx and see what happens
        tx_out = tx_to_validate.txs_out[1]

        disassembly = tools.disassemble(tx_out.script)

        tx_out.script = tools.compile(disassembly)

        tx_to_validate.validate(tx_db)

        disassembly = disassembly.replace("9661a79ae1f6d487af3420c13e649d6df3747fc2", "9661a79ae1f6d487af3420c13e649d6df3747fc3")

        tx_out.script = tools.compile(disassembly)

        with self.assertRaises(ValidationFailureError) as cm:
            tx_to_validate.validate(tx_db)
        exception = cm.exception
        self.assertEqual(exception.args[0], "Tx 3c0ef7e369e81876abb0c870d433c935660126be62a9fd5fef22394d898d1465 TxIn index 0 did not verify")

def main():
    unittest.main()

if __name__ == "__main__":
    main()
