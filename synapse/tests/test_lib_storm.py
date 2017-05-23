import synapse.cortex as s_cortex
import synapse.cores.common as s_common

from synapse.tests.common import *

class StormTest(SynTest):
    def test_storm_cmpr_norm(self):
        with s_cortex.openurl('ram:///') as core:
            core.formTufoByProp('inet:dns:a', 'woot.com/1.2.3.4')
            self.eq(len(core.eval('inet:dns:a:ipv4="1.2.3.4"')), 1)
            self.eq(len(core.eval('inet:dns:a:ipv4="1.2.3.4" -:ipv4="1.2.3.4"')), 0)
            self.eq(len(core.eval('inet:dns:a:ipv4="1.2.3.4" +:ipv4="1.2.3.4"')), 1)

    def test_storm_pivot(self):
        with s_cortex.openurl('ram:///') as core:
            core.formTufoByProp('inet:dns:a', 'woot.com/1.2.3.4')
            core.formTufoByProp('inet:dns:a', 'vertex.vis/5.6.7.8')
            core.formTufoByProp('inet:dns:a', 'vertex.link/5.6.7.8')

            node = core.eval('inet:ipv4="1.2.3.4" inet:ipv4->inet:dns:a:ipv4')[0]

            self.nn(node)
            self.eq(node[1].get('inet:dns:a'), 'woot.com/1.2.3.4')

            node = core.eval('inet:dns:a="woot.com/1.2.3.4" :ipv4->inet:ipv4')[0]

            self.nn(node)
            self.eq(node[1].get('inet:ipv4'), 0x01020304)

            node = core.eval('inet:fqdn="woot.com" ->inet:dns:a:fqdn')[0]

            self.nn(node)
            self.eq(node[1].get('inet:dns:a'), 'woot.com/1.2.3.4')

            self.eq(len(core.eval('inet:dns:a:ipv4="5.6.7.8" :fqdn->inet:fqdn')), 2)

            self.eq(len(core.eval('inet:ipv4="5.6.7.8" -> inet:dns:a:ipv4')), 2)
            self.eq(len(core.eval('inet:ipv4="5.6.7.8" inet:ipv4->inet:dns:a:ipv4')), 2)

    def test_storm_setprop(self):
        with s_cortex.openurl('ram:///') as core:
            core.setConfOpt('enforce',1)

            node = core.formTufoByProp('inet:fqdn', 'vertex.link')

            node = core.eval('inet:fqdn=vertex.link setprop(created="2016-05-05",updated="2017/05/05")')[0]

            self.eq(node[1].get('inet:fqdn'), 'vertex.link')
            self.eq(node[1].get('inet:fqdn:created'), 1462406400000)
            self.eq(node[1].get('inet:fqdn:updated'), 1493942400000)

    def test_storm_filt_regex(self):

        with s_cortex.openurl('ram:///') as core:
            core.setConfOpt('enforce',1)

            iden0 = guid()
            iden1 = guid()
            iden2 = guid()

            node0 = core.formTufoByProp('file:bytes', iden0)
            node1 = core.formTufoByProp('file:bytes', iden1, name='woot.exe')
            node2 = core.formTufoByProp('file:bytes', iden2, name='toow.exe')

            nodes = core.eval('file:bytes +:name~=exe')
            self.eq( len(nodes), 2 )

    def test_storm_alltag(self):

        with s_cortex.openurl('ram:///') as core:
            core.setConfOpt('enforce',1)

            iden = guid()
            node = core.formTufoByProp('inet:fqdn','vertex.link')

            core.addTufoTag(node,'foo.bar')
            core.addTufoTag(node,'baz.faz')

            node = core.eval('#foo.bar')[0]

            self.eq( node[1].get('inet:fqdn'), 'vertex.link' )

            self.nn( node[1].get('*|inet:fqdn|baz') )
            self.nn( node[1].get('*|inet:fqdn|foo.bar') )

    def test_storm_addtag(self):
        with s_cortex.openurl('ram:///') as core:
            iden = guid()
            node = core.formTufoByProp('inet:fqdn', 'vertex.link')

            node = core.eval('inet:fqdn=vertex.link addtag(foo.bar,baz.faz)')[0]

            self.eq(node[1].get('inet:fqdn'), 'vertex.link')

            self.nn(node[1].get('*|inet:fqdn|foo'))
            self.nn(node[1].get('*|inet:fqdn|foo.bar'))
            self.nn(node[1].get('*|inet:fqdn|baz'))
            self.nn(node[1].get('*|inet:fqdn|baz.faz'))

    def test_storm_deltag(self):
        with s_cortex.openurl('ram:///') as core:
            iden = guid()
            node = core.formTufoByProp('inet:fqdn', 'vertex.link')

            core.addTufoTag(node, 'foo.bar')
            core.addTufoTag(node, 'baz.faz')

            node = core.eval('inet:fqdn=vertex.link deltag(foo,baz.faz)')[0]

            self.eq(node[1].get('inet:fqdn'), 'vertex.link')

            self.nn(node[1].get('*|inet:fqdn|baz'))

            self.none(node[1].get('*|inet:fqdn|foo'))
            self.none(node[1].get('*|inet:fqdn|foo.bar'))
            self.none(node[1].get('*|inet:fqdn|baz.faz'))

    def test_storm_refs(self):

        with s_cortex.openurl('ram:///') as core:
            core.setConfOpt('enforce',1)

            iden = guid()
            core.formTufoByProp('inet:dns:a','foo.com/1.2.3.4')
            core.formTufoByProp('inet:dns:a','bar.com/1.2.3.4')

            self.eq( len(core.eval('inet:ipv4=1.2.3.4 refs(in)')), 3 )
            self.eq( len(core.eval('inet:ipv4=1.2.3.4 refs(in,limit=1)')), 2 )

            self.eq( len(core.eval('inet:dns:a=foo.com/1.2.3.4 refs(out)')), 3 )
            self.eq( len(core.eval('inet:dns:a=foo.com/1.2.3.4 refs(out,limit=1)')), 2 )

    def test_storm_tag_query(self):
        # Ensure that non-glob tag filters operate as expected.
        with s_cortex.openurl('ram:///') as core:  # type: s_common.Cortex
            node1 = core.formTufoByProp('inet:dns:a', 'woot.com/1.2.3.4')
            node2 = core.formTufoByProp('inet:dns:a', 'vertex.vis/5.6.7.8')
            node3 = core.formTufoByProp('inet:dns:a', 'vertex.link/5.6.7.8')

            core.addTufoTags(node1, ['aka.foo.bar.baz', 'aka.duck.quack.loud', 'src.clowntown'])
            core.addTufoTags(node2, ['aka.foo.duck.baz', 'aka.duck.quack.loud', 'src.clowntown'])
            core.addTufoTags(node3, ['aka.foo.bar.knight', 'aka.duck.sound.loud', 'src.clowntown'])

            nodes = core.eval('inet:dns:a +#src.clowntown')
            self.eq(len(nodes), 3)

            nodes = core.eval('inet:dns:a +#src')
            self.eq(len(nodes), 3)

            nodes = core.eval('inet:dns:a +#aka.duck.quack')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#aka.foo.bar.knight')
            self.eq(len(nodes), 1)

            nodes = core.eval('inet:dns:a +#src.internet')
            self.eq(len(nodes), 0)

            nodes = core.eval('inet:dns:a -#aka.foo.bar')
            self.eq(len(nodes), 1)

    def test_storm_tag_glob(self):
        # Ensure that glob operators with tag filters operate properly.
        with s_cortex.openurl('ram:///') as core:  # type: s_common.Cortex
            node1 = core.formTufoByProp('inet:dns:a', 'woot.com/1.2.3.4')
            node2 = core.formTufoByProp('inet:dns:a', 'vertex.vis/5.6.7.8')
            node3 = core.formTufoByProp('inet:dns:a', 'vertex.link/5.6.7.8')
            node4 = core.formTufoByProp('inet:dns:a', 'clowntown.link/10.11.12.13')

            core.addTufoTags(node1, ['aka.bar.baz',
                                     'aka.duck.quack.loud',
                                     'src.clowntown',
                                     'loc.milkyway.galactic_arm_a.sol.earth.us.ca.san_francisco'])
            core.addTufoTags(node2, ['aka.duck.baz',
                                     'aka.duck.quack.loud',
                                     'src.clowntown',
                                     'loc.milkyway.galactic_arm_a.sol.earth.us.va.san_francisco'])
            core.addTufoTags(node3, ['aka.bar.knight',
                                     'aka.duck.sound.loud',
                                     'src.clowntown',
                                     'loc.milkyway.galactic_arm_a.sol.earth.us.nv.perfection'])
            core.addTufoTags(node4, ['aka.bar.knightdark',
                                     'aka.duck.sound.loud',
                                     'src.clowntown',
                                     'loc.milkyway.galactic_arm_a.sol.mars.us.tx.perfection'])

            nodes = core.eval('inet:dns:a +#aka.*.baz')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#aka.duck.*.loud')
            self.eq(len(nodes), 4)

            nodes = core.eval('inet:dns:a +#aka.*.sound.loud')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a -#aka.*.baz')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#aka.*.loud')
            self.eq(len(nodes), 0)

            nodes = core.eval('inet:dns:a +#aka.*.*.loud')
            self.eq(len(nodes), 4)

            nodes = core.eval('inet:dns:a +#aka.*.*.*.loud')
            self.eq(len(nodes), 0)

            nodes = core.eval('inet:dns:a +#aka.*.knight')
            self.eq(len(nodes), 1)

            nodes = core.eval('inet:dns:a +#aka.**.loud')
            self.eq(len(nodes), 4)

            nodes = core.eval('inet:dns:a +#loc.**.perfection')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#loc.**.sol.*.us')
            self.eq(len(nodes), 4)

            nodes = core.eval('inet:dns:a +#loc.*.galactic_arm_a.**.us.*.perfection')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#**.baz')
            self.eq(len(nodes), 2)

            nodes = core.eval('inet:dns:a +#**.mars')
            self.eq(len(nodes), 1)

            nodes = core.eval('inet:dns:a -#**.mars.*.tx')
            self.eq(len(nodes), 3)

            nodes = core.eval('inet:dns:a +#loc.milkyway.*arm*.**.tx')
            self.eq(len(nodes), 1)

            nodes = core.eval('inet:dns:a +#loc.**.u*')
            self.eq(len(nodes), 4)

            nodes = core.eval('inet:dns:a +#loc.milkyway.galactic**.tx')
            self.eq(len(nodes), 1)